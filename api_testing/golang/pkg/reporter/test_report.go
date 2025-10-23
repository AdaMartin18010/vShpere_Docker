package main

import (
	"encoding/json"
	"fmt"
	"html/template"
	"os"
	"time"
)

// TestResult 单个测试结果
type TestResult struct {
	Name      string        `json:"name"`
	Package   string        `json:"package"`
	Status    string        `json:"status"` // passed, failed, skipped
	Duration  time.Duration `json:"duration"`
	Error     string        `json:"error,omitempty"`
	Output    string        `json:"output,omitempty"`
	Timestamp time.Time     `json:"timestamp"`
}

// TestSuite 测试套件结果
type TestSuite struct {
	Name      string        `json:"name"`
	Tests     []TestResult  `json:"tests"`
	Total     int           `json:"total"`
	Passed    int           `json:"passed"`
	Failed    int           `json:"failed"`
	Skipped   int           `json:"skipped"`
	Duration  time.Duration `json:"duration"`
	Timestamp time.Time     `json:"timestamp"`
}

// TestReport 完整测试报告
type TestReport struct {
	ProjectName string          `json:"project_name"`
	Version     string          `json:"version"`
	Timestamp   time.Time       `json:"timestamp"`
	Suites      []TestSuite     `json:"suites"`
	Summary     TestSummary     `json:"summary"`
	Environment TestEnvironment `json:"environment"`
}

// TestSummary 测试摘要
type TestSummary struct {
	TotalTests    int           `json:"total_tests"`
	TotalPassed   int           `json:"total_passed"`
	TotalFailed   int           `json:"total_failed"`
	TotalSkipped  int           `json:"total_skipped"`
	TotalDuration time.Duration `json:"total_duration"`
	PassRate      float64       `json:"pass_rate"`
}

// TestEnvironment 测试环境信息
type TestEnvironment struct {
	GoVersion     string `json:"go_version"`
	OS            string `json:"os"`
	Architecture  string `json:"architecture"`
	DockerVersion string `json:"docker_version,omitempty"`
	K8sVersion    string `json:"k8s_version,omitempty"`
}

// GenerateHTMLReport 生成HTML测试报告
func GenerateHTMLReport(report *TestReport, outputPath string) error {
	tmpl := `<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>API测试报告 - {{.ProjectName}}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.1em; opacity: 0.9; }
        .summary {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f7fafc;
        }
        .metric {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }
        .metric h3 { color: #4a5568; font-size: 0.9em; margin-bottom: 10px; }
        .metric p { font-size: 2em; font-weight: bold; }
        .metric.passed p { color: #48bb78; }
        .metric.failed p { color: #f56565; }
        .metric.skipped p { color: #ed8936; }
        .metric.total p { color: #4299e1; }
        .metric.rate p { color: #9f7aea; }
        .suite {
            margin: 20px 30px;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
        }
        .suite-header {
            background: #edf2f7;
            padding: 15px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .suite-header:hover { background: #e2e8f0; }
        .suite-header h2 { font-size: 1.3em; color: #2d3748; }
        .suite-stats {
            display: flex;
            gap: 15px;
            font-size: 0.9em;
        }
        .stat { padding: 5px 10px; border-radius: 5px; }
        .stat.passed { background: #c6f6d5; color: #22543d; }
        .stat.failed { background: #fed7d7; color: #742a2a; }
        .stat.skipped { background: #feebc8; color: #7c2d12; }
        .tests {
            padding: 20px;
            display: none;
        }
        .tests.show { display: block; }
        .test {
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid;
            background: #f7fafc;
            border-radius: 5px;
        }
        .test.passed { border-color: #48bb78; }
        .test.failed { border-color: #f56565; }
        .test.skipped { border-color: #ed8936; }
        .test-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 5px;
        }
        .test-name { font-weight: bold; color: #2d3748; }
        .test-duration { color: #718096; font-size: 0.9em; }
        .test-error {
            margin-top: 10px;
            padding: 10px;
            background: #fff5f5;
            border-left: 3px solid #f56565;
            color: #742a2a;
            font-family: monospace;
            font-size: 0.85em;
            white-space: pre-wrap;
        }
        .environment {
            background: #f7fafc;
            padding: 20px 30px;
            margin: 20px 30px;
            border-radius: 8px;
        }
        .environment h3 { margin-bottom: 15px; color: #2d3748; }
        .env-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 10px;
        }
        .env-item { padding: 10px; background: white; border-radius: 5px; }
        .env-item strong { color: #4a5568; }
        .footer {
            text-align: center;
            padding: 20px;
            color: #718096;
            font-size: 0.9em;
        }
        .toggle-icon {
            transition: transform 0.3s;
        }
        .toggle-icon.rotate { transform: rotate(180deg); }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧪 API测试报告</h1>
            <p>{{.ProjectName}} - 版本 {{.Version}}</p>
            <p style="font-size: 0.9em; margin-top: 10px;">生成时间: {{.Timestamp.Format "2006-01-02 15:04:05"}}</p>
        </div>

        <div class="summary">
            <div class="metric total">
                <h3>总测试数</h3>
                <p>{{.Summary.TotalTests}}</p>
            </div>
            <div class="metric passed">
                <h3>通过</h3>
                <p>{{.Summary.TotalPassed}}</p>
            </div>
            <div class="metric failed">
                <h3>失败</h3>
                <p>{{.Summary.TotalFailed}}</p>
            </div>
            <div class="metric skipped">
                <h3>跳过</h3>
                <p>{{.Summary.TotalSkipped}}</p>
            </div>
            <div class="metric rate">
                <h3>通过率</h3>
                <p>{{printf "%.1f" .Summary.PassRate}}%</p>
            </div>
            <div class="metric">
                <h3>总耗时</h3>
                <p style="color: #667eea; font-size: 1.5em;">{{.Summary.TotalDuration}}</p>
            </div>
        </div>

        <div class="environment">
            <h3>🔧 测试环境</h3>
            <div class="env-grid">
                <div class="env-item"><strong>Go版本:</strong> {{.Environment.GoVersion}}</div>
                <div class="env-item"><strong>操作系统:</strong> {{.Environment.OS}}</div>
                <div class="env-item"><strong>架构:</strong> {{.Environment.Architecture}}</div>
                {{if .Environment.DockerVersion}}
                <div class="env-item"><strong>Docker:</strong> {{.Environment.DockerVersion}}</div>
                {{end}}
                {{if .Environment.K8sVersion}}
                <div class="env-item"><strong>Kubernetes:</strong> {{.Environment.K8sVersion}}</div>
                {{end}}
            </div>
        </div>

        {{range .Suites}}
        <div class="suite">
            <div class="suite-header" onclick="toggleSuite(this)">
                <h2>📦 {{.Name}}</h2>
                <div style="display: flex; align-items: center; gap: 15px;">
                    <div class="suite-stats">
                        <span class="stat passed">✓ {{.Passed}}</span>
                        {{if gt .Failed 0}}<span class="stat failed">✗ {{.Failed}}</span>{{end}}
                        {{if gt .Skipped 0}}<span class="stat skipped">⊘ {{.Skipped}}</span>{{end}}
                    </div>
                    <span class="toggle-icon">▼</span>
                </div>
            </div>
            <div class="tests">
                {{range .Tests}}
                <div class="test {{.Status}}">
                    <div class="test-header">
                        <span class="test-name">
                            {{if eq .Status "passed"}}✅{{else if eq .Status "failed"}}❌{{else}}⊘{{end}}
                            {{.Name}}
                        </span>
                        <span class="test-duration">{{.Duration}}</span>
                    </div>
                    {{if .Error}}
                    <div class="test-error">{{.Error}}</div>
                    {{end}}
                </div>
                {{end}}
            </div>
        </div>
        {{end}}

        <div class="footer">
            <p>由 Go API 测试套件生成 | GitHub Actions CI/CD</p>
        </div>
    </div>

    <script>
        function toggleSuite(header) {
            const tests = header.nextElementSibling;
            const icon = header.querySelector('.toggle-icon');
            tests.classList.toggle('show');
            icon.classList.toggle('rotate');
        }
    </script>
</body>
</html>`

	t, err := template.New("report").Parse(tmpl)
	if err != nil {
		return err
	}

	f, err := os.Create(outputPath)
	if err != nil {
		return err
	}
	defer f.Close()

	return t.Execute(f, report)
}

// GenerateJSONReport 生成JSON测试报告
func GenerateJSONReport(report *TestReport, outputPath string) error {
	data, err := json.MarshalIndent(report, "", "  ")
	if err != nil {
		return err
	}

	return os.WriteFile(outputPath, data, 0644)
}

// GenerateMarkdownReport 生成Markdown测试报告
func GenerateMarkdownReport(report *TestReport, outputPath string) error {
	content := fmt.Sprintf(`# API测试报告

## 项目信息
- **项目名称**: %s
- **版本**: %s
- **生成时间**: %s

## 测试摘要

| 指标 | 数值 |
|------|------|
| 总测试数 | %d |
| 通过 | ✅ %d |
| 失败 | ❌ %d |
| 跳过 | ⊘ %d |
| 通过率 | %.1f%% |
| 总耗时 | %s |

## 测试环境

- **Go版本**: %s
- **操作系统**: %s
- **架构**: %s
`, report.ProjectName, report.Version, report.Timestamp.Format("2006-01-02 15:04:05"),
		report.Summary.TotalTests,
		report.Summary.TotalPassed,
		report.Summary.TotalFailed,
		report.Summary.TotalSkipped,
		report.Summary.PassRate,
		report.Summary.TotalDuration,
		report.Environment.GoVersion,
		report.Environment.OS,
		report.Environment.Architecture)

	if report.Environment.DockerVersion != "" {
		content += fmt.Sprintf("- **Docker**: %s\n", report.Environment.DockerVersion)
	}
	if report.Environment.K8sVersion != "" {
		content += fmt.Sprintf("- **Kubernetes**: %s\n", report.Environment.K8sVersion)
	}

	content += "\n## 详细测试结果\n\n"

	for _, suite := range report.Suites {
		content += fmt.Sprintf("### %s\n\n", suite.Name)
		content += fmt.Sprintf("- **总数**: %d\n", suite.Total)
		content += fmt.Sprintf("- **通过**: %d\n", suite.Passed)
		content += fmt.Sprintf("- **失败**: %d\n", suite.Failed)
		content += fmt.Sprintf("- **跳过**: %d\n", suite.Skipped)
		content += fmt.Sprintf("- **耗时**: %s\n\n", suite.Duration)

		content += "| 测试名称 | 状态 | 耗时 |\n"
		content += "|---------|------|------|\n"

		for _, test := range suite.Tests {
			status := ""
			switch test.Status {
			case "passed":
				status = "✅ 通过"
			case "failed":
				status = "❌ 失败"
			case "skipped":
				status = "⊘ 跳过"
			}
			content += fmt.Sprintf("| %s | %s | %s |\n", test.Name, status, test.Duration)
		}

		content += "\n"
	}

	return os.WriteFile(outputPath, []byte(content), 0644)
}

// CreateSampleReport 创建示例报告
func CreateSampleReport() *TestReport {
	now := time.Now()

	return &TestReport{
		ProjectName: "vSphere_Docker API Tests",
		Version:     "1.0.0",
		Timestamp:   now,
		Suites: []TestSuite{
			{
				Name: "Docker API Tests",
				Tests: []TestResult{
					{
						Name:      "Test01_GetDockerVersion",
						Package:   "main",
						Status:    "passed",
						Duration:  time.Millisecond * 245,
						Timestamp: now,
					},
					{
						Name:      "Test02_GetDockerInfo",
						Package:   "main",
						Status:    "passed",
						Duration:  time.Millisecond * 312,
						Timestamp: now,
					},
				},
				Total:     20,
				Passed:    20,
				Failed:    0,
				Skipped:   0,
				Duration:  time.Second * 8,
				Timestamp: now,
			},
		},
		Summary: TestSummary{
			TotalTests:    51,
			TotalPassed:   51,
			TotalFailed:   0,
			TotalSkipped:  0,
			TotalDuration: time.Second * 25,
			PassRate:      100.0,
		},
		Environment: TestEnvironment{
			GoVersion:     "1.21.4",
			OS:            "linux",
			Architecture:  "amd64",
			DockerVersion: "24.0.7",
			K8sVersion:    "1.28.0",
		},
	}
}
