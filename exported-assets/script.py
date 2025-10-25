
# Create the professional NeuraShield.AI website files

# HTML Content
html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NeuraShield.AI - Enterprise Code Security Platform</title>
    <link rel="stylesheet" href="home.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Poppins:wght@400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css">
</head>
<body>
    <!-- Professional Header -->
    <header class="main-header">
        <div class="container-header">
            <div class="logo">
                <span class="logo-icon">🛡️</span>
                <span class="logo-text">NeuraShield.AI</span>
            </div>
            <nav class="main-nav">
                <a href="#dashboard" class="nav-link active">Dashboard</a>
                <a href="#reports" class="nav-link">Reports</a>
                <a href="#analytics" class="nav-link">Analytics</a>
                <a href="#compliance" class="nav-link">Compliance</a>
                <a href="#settings" class="nav-link">Settings</a>
            </nav>
            <div class="header-actions">
                <button class="icon-btn" aria-label="Search">🔍</button>
                <button class="icon-btn" aria-label="Notifications">🔔</button>
                <div class="user-avatar">👤</div>
            </div>
        </div>
    </header>

    <!-- Hero Section -->
    <section class="hero-section">
        <div class="hero-content">
            <h1 class="hero-title">NeuraShield.AI</h1>
            <p class="hero-tagline">Enterprise-Grade Code Security & Vulnerability Assessment Platform</p>
            <div class="hero-stats">
                <div class="stat-item">
                    <div class="stat-value">12,847+</div>
                    <div class="stat-label">Analyses</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">99.9%</div>
                    <div class="stat-label">Accuracy</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">24/7</div>
                    <div class="stat-label">Monitoring</div>
                </div>
            </div>
            <div class="hero-cta">
                <button class="btn btn-primary">Start Analysis</button>
                <button class="btn btn-secondary">View Demo</button>
            </div>
        </div>
    </section>

    <!-- Dashboard KPI Section -->
    <section class="dashboard-section" id="dashboard">
        <div class="container">
            <div class="kpi-grid">
                <div class="kpi-card">
                    <div class="kpi-icon">📊</div>
                    <div class="kpi-content">
                        <div class="kpi-value">1,247</div>
                        <div class="kpi-label">Total Vulnerabilities</div>
                        <div class="kpi-trend positive">↑ 5.2%</div>
                    </div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-icon">✅</div>
                    <div class="kpi-content">
                        <div class="kpi-value">95%</div>
                        <div class="kpi-label">Issues Resolved</div>
                        <div class="kpi-progress">
                            <div class="progress-bar" style="width: 95%"></div>
                        </div>
                    </div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-icon">🛡️</div>
                    <div class="kpi-content">
                        <div class="kpi-value">8.1/10</div>
                        <div class="kpi-label">Security Score</div>
                        <div class="score-indicator">
                            <div class="score-circle" data-score="81"></div>
                        </div>
                    </div>
                </div>
                <div class="kpi-card">
                    <div class="kpi-icon">📋</div>
                    <div class="kpi-content">
                        <div class="kpi-value">SOC 2</div>
                        <div class="kpi-label">Compliance Status</div>
                        <div class="compliance-badge">Compliant ✓</div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Reports Carousel Section -->
    <section class="reports-section" id="reports">
        <div class="container">
            <h2 class="section-title">Recent Analysis Reports</h2>
            <div class="swiper reports-carousel">
                <div class="swiper-wrapper">
                    <!-- Report Card 1 -->
                    <div class="swiper-slide">
                        <div class="report-card" data-report="1">
                            <div class="report-header">
                                <div class="report-icon">🔒</div>
                                <span class="report-time">Today, 3:30 PM</span>
                            </div>
                            <h3 class="report-title">Flask Security Audit</h3>
                            <div class="report-meta">
                                <span>1,247 lines</span>
                                <span>•</span>
                                <span>23 files</span>
                            </div>
                            <div class="badge-group">
                                <span class="badge badge-high">HIGH Risk</span>
                                <span class="badge badge-info">1 Bug Found</span>
                            </div>
                            <div class="report-score">
                                <div class="score-label">CVSS Score</div>
                                <div class="score-value">8.1/10</div>
                            </div>
                            <button class="btn-view-report">View Report →</button>
                        </div>
                    </div>

                    <!-- Report Card 2 -->
                    <div class="swiper-slide">
                        <div class="report-card" data-report="2">
                            <div class="report-header">
                                <div class="report-icon">🔒</div>
                                <span class="report-time">Today, 2:15 PM</span>
                            </div>
                            <h3 class="report-title">API Security Review</h3>
                            <div class="report-meta">
                                <span>892 lines</span>
                                <span>•</span>
                                <span>15 files</span>
                            </div>
                            <div class="badge-group">
                                <span class="badge badge-low">LOW Risk</span>
                                <span class="badge badge-success">0 Bugs</span>
                            </div>
                            <div class="report-score">
                                <div class="score-label">CVSS Score</div>
                                <div class="score-value">9.2/10</div>
                            </div>
                            <button class="btn-view-report">View Report →</button>
                        </div>
                    </div>

                    <!-- Report Card 3 -->
                    <div class="swiper-slide">
                        <div class="report-card" data-report="3">
                            <div class="report-header">
                                <div class="report-icon">🔒</div>
                                <span class="report-time">Today, 11:45 AM</span>
                            </div>
                            <h3 class="report-title">E-commerce Backend</h3>
                            <div class="report-meta">
                                <span>2,156 lines</span>
                                <span>•</span>
                                <span>45 files</span>
                            </div>
                            <div class="badge-group">
                                <span class="badge badge-medium">MEDIUM Risk</span>
                                <span class="badge badge-warning">3 Bugs Found</span>
                            </div>
                            <div class="report-score">
                                <div class="score-label">CVSS Score</div>
                                <div class="score-value">6.3/10</div>
                            </div>
                            <button class="btn-view-report">View Report →</button>
                        </div>
                    </div>
                </div>
                <div class="swiper-button-prev"></div>
                <div class="swiper-button-next"></div>
                <div class="swiper-pagination"></div>
            </div>
        </div>
    </section>

    <!-- Detailed Report Modal -->
    <div class="report-modal" id="reportModal">
        <div class="modal-overlay"></div>
        <div class="modal-content">
            <div class="modal-header">
                <h2 class="modal-title">Analysis Report</h2>
                <button class="modal-close">✕</button>
            </div>
            <div class="modal-body">
                <div class="report-details-grid">
                    <!-- Bug Detection -->
                    <div class="detail-section">
                        <h3 class="detail-title">🐛 Bug Detection</h3>
                        <div class="bugs-list" id="bugsList"></div>
                    </div>

                    <!-- Code Optimization -->
                    <div class="detail-section">
                        <h3 class="detail-title">⚡ Code Optimization</h3>
                        <div class="optimization-content" id="optimizationContent"></div>
                    </div>

                    <!-- Security Scoring -->
                    <div class="detail-section">
                        <h3 class="detail-title">🛡️ Security Scoring</h3>
                        <div class="security-content" id="securityContent"></div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Features Section -->
    <section class="features-section">
        <div class="container">
            <h2 class="section-title">Enterprise Features</h2>
            <div class="features-grid">
                <div class="feature-card">
                    <div class="feature-icon">🔍</div>
                    <h3 class="feature-title">Automated Security Scanning</h3>
                    <p class="feature-description">Continuous monitoring with automated vulnerability detection across your entire codebase using advanced pattern recognition.</p>
                    <div class="feature-metric">10K+ scans daily</div>
                    <button class="btn btn-outline">Learn More</button>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">📊</div>
                    <h3 class="feature-title">CVSS 3.1 Compliance</h3>
                    <p class="feature-description">Industry-standard vulnerability scoring with detailed risk assessment and priority-based remediation guidance.</p>
                    <div class="feature-metric">99.9% accuracy rating</div>
                    <button class="btn btn-outline">Learn More</button>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">⚙️</div>
                    <h3 class="feature-title">Enterprise Integration</h3>
                    <p class="feature-description">Seamless integration with CI/CD pipelines, ticketing systems, and development workflows.</p>
                    <div class="feature-metric">50+ integrations</div>
                    <button class="btn btn-outline">Learn More</button>
                </div>

                <div class="feature-card">
                    <div class="feature-icon">📋</div>
                    <h3 class="feature-title">Compliance Reporting</h3>
                    <p class="feature-description">Automated compliance reports for SOC 2, GDPR, HIPAA, and other regulatory frameworks.</p>
                    <div class="feature-metric">Real-time tracking</div>
                    <button class="btn btn-outline">Learn More</button>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="main-footer">
        <div class="container">
            <div class="footer-content">
                <p>© 2025 NeuraShield.AI | Advanced Security Analysis</p>
                <div class="footer-links">
                    <a href="#privacy">Privacy Policy</a>
                    <a href="#terms">Terms of Service</a>
                    <a href="#contact">Contact Us</a>
                </div>
            </div>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
    <script src="home.js"></script>
</body>
</html>'''

# Save HTML file
with open('home.html', 'w', encoding='utf-8') as f:
    f.write(html_content)

print("✅ home.html file created successfully!")
print(f"File size: {len(html_content)} characters")
