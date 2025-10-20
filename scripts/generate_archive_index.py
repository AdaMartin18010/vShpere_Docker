import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "_archive"

HEADER = """# {month} 归档文档索引

> **归档生成时间**: {now}

---

## 📋 目录

- [{month} 归档文档索引](#{anchor})
  - [📋 目录](#-目录)
  - [1. 归档说明](#1-归档说明)
  - [2. 文档分类](#2-文档分类)
    - [2.1 每日工作总结 (daily_summaries/)](#21-每日工作总结-daily_summaries)
    - [2.2 里程碑报告 (milestone_reports/)](#22-里程碑报告-milestone_reports)
    - [2.3 专题总结 (project_summaries/)](#23-专题总结-project_summaries)
  - [3. 统计](#3-统计)
"""

BODY_EXPLAIN = """
---

## 1. 归档说明

本目录包含 {month} 期间的历史总结与报告，按类型分类存放：

```text
{ym}/
├── daily_summaries/
├── milestone_reports/
└── project_summaries/
```

---

## 2. 文档分类

### 2.1 每日工作总结 (daily_summaries/)

{daily_list}

### 2.2 里程碑报告 (milestone_reports/)

{milestone_list}

### 2.3 专题总结 (project_summaries/)

{project_list}

---

## 3. 统计

- 每日工作总结: {daily_count} 个
- 里程碑报告: {milestone_count} 个
- 专题总结: {project_count} 个
- 总计: {total_count} 个
"""


def list_files(dir_path: Path) -> list[str]:
    if not dir_path.exists():
        return []
    return [f.name for f in sorted(dir_path.glob("*.md"))]


def md_list(items: list[str]) -> str:
    if not items:
        return "(空)"
    return "\n".join(f"- {name}" for name in items)


def generate_for_month(month_dir: Path):
    ym = month_dir.name
    month = f"{ym[:4]}年{ym[5:]}月"
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    anchor = f"{ym}年归档文档索引"  # 仅作为占位

    daily = list_files(month_dir / "daily_summaries")
    milestone = list_files(month_dir / "milestone_reports")
    project = list_files(month_dir / "project_summaries")

    daily_count = len(daily)
    milestone_count = len(milestone)
    project_count = len(project)
    total_count = daily_count + milestone_count + project_count

    readme = HEADER.format(month=f"{ym} {month}", now=now, anchor=anchor)
    readme += BODY_EXPLAIN.format(
        month=f"{ym} {month}", ym=ym,
        daily_list=md_list(daily),
        milestone_list=md_list(milestone),
        project_list=md_list(project),
        daily_count=daily_count,
        milestone_count=milestone_count,
        project_count=project_count,
        total_count=total_count,
    )

    (month_dir / "README.generated.md").write_text(readme, encoding="utf-8")
    print(f"Generated: {month_dir / 'README.generated.md'}")


def main():
    if not ARCHIVE.exists():
        print("_archive directory not found.")
        return
    for month_dir in sorted(ARCHIVE.iterdir()):
        if not month_dir.is_dir():
            continue
        # expect YYYY-MM
        if len(month_dir.name) == 7 and month_dir.name[4] == '-':
            generate_for_month(month_dir)


if __name__ == "__main__":
    main()
