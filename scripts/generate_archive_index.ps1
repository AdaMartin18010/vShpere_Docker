param(
  [string]$ArchiveRoot = "_archive"
)

function Get-MdList($items) {
  if (-not $items -or $items.Count -eq 0) { return "(空)" }
  return ($items | ForEach-Object { "- $_" }) -join "`n"
}

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location (Join-Path $root "..")

if (-not (Test-Path $ArchiveRoot)) {
  Write-Host "Archive directory not found: $ArchiveRoot" -ForegroundColor Yellow
  exit 0
}

Get-ChildItem -Path $ArchiveRoot -Directory | Where-Object { $_.Name -match '^[0-9]{4}-[0-9]{2}$' } | ForEach-Object {
  $monthDir = $_.FullName
  $ym = $_.Name
  $monthCN = "{0}年{1}月" -f $ym.Substring(0,4), $ym.Substring(5,2)
  $now = (Get-Date).ToString('yyyy-MM-dd HH:mm')

  $daily = Get-ChildItem -Path (Join-Path $monthDir 'daily_summaries') -Filter *.md -File -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name | Sort-Object
  $milestone = Get-ChildItem -Path (Join-Path $monthDir 'milestone_reports') -Filter *.md -File -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name | Sort-Object
  $project = Get-ChildItem -Path (Join-Path $monthDir 'project_summaries') -Filter *.md -File -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name | Sort-Object

  $dailyCount = ($daily | Measure-Object).Count
  $milestoneCount = ($milestone | Measure-Object).Count
  $projectCount = ($project | Measure-Object).Count
  $totalCount = $dailyCount + $milestoneCount + $projectCount

  $header = @"
# $ym $monthCN 归档文档索引

> **归档生成时间**: $now

---

## 📋 目录

- [$ym $monthCN 归档文档索引](#$ym-$monthCN-归档文档索引)
  - [📋 目录](#-目录)
  - [1. 归档说明](#1-归档说明)
  - [2. 文档分类](#2-文档分类)
    - [2.1 每日工作总结 (daily_summaries/)](#21-每日工作总结-daily_summaries)
    - [2.2 里程碑报告 (milestone_reports/)](#22-里程碑报告-milestone_reports)
    - [2.3 专题总结 (project_summaries/)](#23-专题总结-project_summaries)
  - [3. 统计](#3-统计)
"@

  $body = @"
---

## 1. 归档说明

本目录包含 $ym $monthCN 期间的历史总结与报告，按类型分类存放：

```text
$ym/
├── daily_summaries/
├── milestone_reports/
└── project_summaries/
```

---

## 2. 文档分类

### 2.1 每日工作总结 (daily_summaries/)

$(Get-MdList $daily)

### 2.2 里程碑报告 (milestone_reports/)

$(Get-MdList $milestone)

### 2.3 专题总结 (project_summaries/)

$(Get-MdList $project)

---

## 3. 统计

- 每日工作总结: $dailyCount 个
- 里程碑报告: $milestoneCount 个
- 专题总结: $projectCount 个
- 总计: $totalCount 个
"@

  $outPath = Join-Path $monthDir 'README.generated.md'
  ($header + "`n" + $body) | Out-File -FilePath $outPath -Encoding utf8 -Force
  Write-Host "Generated: $outPath" -ForegroundColor Green
}
