#!/usr/bin/env python3
import sys
import argparse
import json
from pathlib import Path
from typing import List, Dict, Any, Optional

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from utils.config_manager import ConfigManager, ConfigurationError
from utils.date_utils import validate_years, get_year_range
from utils.output_formatter import (
    format_json_output,
    sort_literature,
    deduplicate_by_doi,
    save_json_output,
    validate_output
)

from api_clients.openalex_client import OpenAlexClient, OpenAlexError, RateLimitError as OpenAlexRateLimit
from api_clients.elsevier_client import ElsevierClient, ElsevierError, RateLimitError as ElsevierRateLimit
from api_clients.wos_client import WOSClient, WOSError, RateLimitError as WOSRateLimit

from parsers.bibtex_parser import BibTeXParser, BibTeXError
from parsers.ris_parser import RISParser, RISError
from parsers.csv_parser import CSVParser, CSVError


class LiteratureCollectorError(Exception):
    pass


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Literature Collector - 搜集中英文顶刊相关研究文献',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='示例:\n'
               '  python main.py --research_field "机器学习" --years 3\n'
               '  python main.py -rf "深度学习" -y 2 -s openalex,elsevier -m 100'
    )

    parser.add_argument(
        '-rf', '--research_field',
        default='',
        help='研究领域关键词'
    )

    parser.add_argument(
        '-y', '--years',
        type=int,
        default=3,
        choices=[1, 2, 3, 4, 5],
        help='搜集最近多少年的文献（1-5年，默认3）'
    )

    parser.add_argument(
        '-s', '--sources',
        default='openalex',
        help='数据源，用逗号分隔（openalex, elsevier, wos, web, file，默认openalex）'
    )

    parser.add_argument(
        '-f', '--file_path',
        help='本地文献文件（当sources包含file时必需）'
    )

    parser.add_argument(
        '-m', '--max_results',
        type=int,
        default=50,
        help='每个数据源返回的最大结果数（默认50）'
    )

    parser.add_argument(
        '-o', '--output_file',
        help='输出文件路径（可选）'
    )

    parser.add_argument(
        '--sort',
        default='citations',
        choices=['citations', 'year', 'title'],
        help='排序方式（citations/year/title，默认citations）'
    )

    parser.add_argument(
        '--no-deduplicate',
        action='store_true',
        help='不进行去重'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='详细输出'
    )

    return parser.parse_args()


def initialize_clients(
    sources: List[str],
    config: ConfigManager,
    max_results: int,
    verbose: bool = False
) -> Dict[str, Any]:
    clients = {}

    if verbose:
        print(f"初始化数据源: {', '.join(sources)}")

    for source in sources:
        source = source.lower().strip()

        try:
            if source == 'openalex':
                timeout = config.get_request_timeout()
                clients['openalex'] = OpenAlexClient(timeout=timeout)
                if verbose:
                    print("  - OpenAlex客户端已初始化")

            elif source == 'elsevier':
                api_key = config.get_api_key('elsevier')
                endpoint = config.get_endpoint('elsevier')
                timeout = config.get_request_timeout()
                clients['elsevier'] = ElsevierClient(api_key, endpoint, timeout)
                if verbose:
                    print("  - Elsevier客户端已初始化")

            elif source == 'wos':
                api_key = config.get_api_key('wos')
                endpoint = config.get_endpoint('wos')
                timeout = config.get_request_timeout()
                clients['wos'] = WOSClient(api_key, endpoint, timeout)
                if verbose:
                    print("  - Web of Science客户端已初始化")

            elif source == 'file':
                clients['file'] = 'file'
                if verbose:
                    print("  - 文件解析器已准备")

            elif source == 'web':
                clients['web'] = 'web'
                if verbose:
                    print("  - 联网搜索已准备")

            else:
                print(f"  警告: 不支持的数据源 '{source}'，已跳过")

        except ConfigurationError as e:
            print(f"  错误: {source} 配置错误 - {str(e)}")
        except Exception as e:
            print(f"  错误: {source} 初始化失败 - {str(e)}")

    return clients


def search_with_fallback(
    clients: Dict[str, Any],
    research_field: str,
    years: int,
    max_results: int,
    file_path: Optional[str] = None,
    verbose: bool = False
) -> List[Dict[str, Any]]:
    results = []
    failed_sources = []

    source_fallback_map = {
        'elsevier': ['openalex', 'web'],
        'wos': ['openalex', 'elsevier', 'web'],
        'openalex': ['web'],
        'web': ['file']
    }

    for source in clients.keys():
        try:
            if verbose:
                print(f"正在从 {source} 搜索文献...")

            if source == 'openalex':
                literature = clients['openalex'].search(research_field, years, max_results)
                results.extend(literature)

            elif source == 'elsevier':
                literature = clients['elsevier'].search(research_field, years, max_results)
                results.extend(literature)

            elif source == 'wos':
                literature = clients['wos'].search(research_field, years, max_results)
                results.extend(literature)

            elif source == 'file':
                if not file_path:
                    print("  错误: 文件路径未提供")
                    continue

                literature = read_local_file(file_path)
                results.extend(literature)

            elif source == 'web':
                print("  注意: 联网搜索功能需要WebSearch工具，暂不支持")
                continue

            if verbose:
                print(f"  成功: 从 {source} 获取 {len(literature)} 篇文献")

        except (OpenAlexRateLimit, ElsevierRateLimit, WOSRateLimit) as e:
            print(f"  速率限制: {source} - {str(e)}")
            failed_sources.append(source)

            fallbacks = source_fallback_map.get(source, [])
            available_fallbacks = [f for f in fallbacks if f in clients and f not in failed_sources]

            if available_fallbacks:
                print(f"  将尝试降级到: {', '.join(available_fallbacks)}")

        except (OpenAlexError, ElsevierError, WOSError) as e:
            print(f"  错误: {source} - {str(e)}")
            failed_sources.append(source)

            fallbacks = source_fallback_map.get(source, [])
            available_fallbacks = [f for f in fallbacks if f in clients and f not in failed_sources]

            if available_fallbacks:
                print(f"  将尝试降级到: {', '.join(available_fallbacks)}")

        except Exception as e:
            print(f"  未知错误: {source} - {str(e)}")
            failed_sources.append(source)

    if not results:
        raise LiteratureCollectorError("所有数据源均失败，无法获取文献")

    return results


def read_local_file(file_path: str) -> List[Dict[str, Any]]:
    path = Path(file_path)

    if not path.exists():
        raise LiteratureCollectorError(f"文件不存在: {file_path}")

    suffix = path.suffix.lower()

    if suffix == '.bib' or suffix == '.bibtex':
        parser = BibTeXParser()
        return parser.parse_file(file_path)

    elif suffix == '.ris':
        parser = RISParser()
        return parser.parse_file(file_path)

    elif suffix == '.csv':
        parser = CSVParser()
        return parser.parse_file(file_path)

    else:
        try:
            content = path.read_text(encoding='utf-8')

            if '@' in content[:100] and '{' in content[:100]:
                parser = BibTeXParser()
                return parser.parse_string(content)

            elif 'TY' in content[:100]:
                parser = RISParser()
                return parser.parse_string(content)

            else:
                parser = CSVParser()
                return parser.parse_string(content)

        except Exception as e:
            raise LiteratureCollectorError(f"无法识别文件格式: {str(e)}")


def main():
    try:
        args = parse_arguments()

        if not validate_years(args.years):
            print("错误: years参数必须是1-5之间的整数")
            sys.exit(1)

        if args.verbose:
            print("加载配置...")
            print(f"研究领域: {args.research_field}")
            print(f"年份范围: {args.years}")

        config = ConfigManager()

        sources = [s.strip() for s in args.sources.split(',')]
        sources = [s for s in sources if s]

        if not sources:
            sources = ['openalex']

        if 'file' in sources and not args.file_path:
            print("错误: 使用file数据源时必须提供--file_path参数")
            sys.exit(1)

        if not args.research_field and 'file' not in sources:
            print("错误: 使用非file数据源时必须提供--research_field参数")
            sys.exit(1)

        clients = initialize_clients(sources, config, args.max_results, args.verbose)

        if not clients:
            print("错误: 没有可用的数据源")
            sys.exit(1)

        if args.verbose:
            print("\n开始搜索文献...")
            print(f"年份范围: {get_year_range(args.years)}")

        literature = search_with_fallback(
            clients,
            args.research_field,
            args.years,
            args.max_results,
            args.file_path,
            args.verbose
        )

        if not args.no_deduplicate:
            if args.verbose:
                print(f"\n去重前: {len(literature)} 篇文献")
            literature = deduplicate_by_doi(literature)
            if args.verbose:
                print(f"去重后: {len(literature)} 篇文献")

        literature = sort_literature(literature, args.sort, reverse=True)

        search_params = {
            'research_field': args.research_field,
            'years': args.years,
            'sources': [get_source_display_name(s) for s in sources]
        }

        output = format_json_output(literature, search_params, config.get_config())

        if not validate_output(output):
            print("警告: 输出格式验证失败")

        if args.output_file:
            save_json_output(output, args.output_file)
            print(f"\n结果已保存到: {args.output_file}")

        print(output)

        if args.verbose:
            data = json.loads(output)
            summary = data['summary']
            print(f"\n统计信息:")
            print(f"  总文献数: {summary['total_results']}")
            print(f"  唯一DOI数: {summary['unique_dois']}")
            print(f"  平均引用次数: {summary['average_citations']}")
            if summary['by_source']:
                print(f"  各数据源:")
                for source, count in summary['by_source'].items():
                    print(f"    {source}: {count}")

    except ConfigurationError as e:
        print(f"配置错误: {str(e)}")
        sys.exit(1)

    except LiteratureCollectorError as e:
        print(f"错误: {str(e)}")
        sys.exit(1)

    except KeyboardInterrupt:
        print("\n操作已取消")
        sys.exit(130)

    except Exception as e:
        print(f"未知错误: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def get_source_display_name(source: str) -> str:
    source_map = {
        'openalex': 'OpenAlex',
        'elsevier': 'Elsevier',
        'wos': 'Web of Science',
        'web': 'Web Search',
        'file': 'Local File'
    }
    return source_map.get(source.lower(), source.capitalize())


if __name__ == '__main__':
    main()
