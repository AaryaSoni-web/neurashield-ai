
# CSS Content
css_content = '''/* ========================================
   NeuraShield.AI - Professional Stylesheet
   ======================================== */

/* CSS Variables */
:root {
    /* Colors */
    --primary-blue: #0A2540;
    --dark-navy: #1A1D29;
    --professional-cyan: #00D4FF;
    --slate-gray: #334155;
    --muted-text: #64748B;
    --white: #FFFFFF;
    
    /* Status Colors */
    --critical: #DC2626;
    --high: #EA580C;
    --medium: #D97706;
    --low: #059669;
    --info: #2563EB;
    --success: #10B981;
    
    /* Gradients */
    --hero-gradient: linear-gradient(135deg, #0A2540 0%, #1A1D29 50%, #000814 100%);
    --card-gradient: linear-gradient(145deg, #1E293B 0%, #0F172A 100%);
    
    /* Spacing */
    --spacing-xs: 4px;
    --spacing-sm: 8px;
    --spacing-md: 16px;
    --spacing-lg: 24px;
    --spacing-xl: 32px;
    --spacing-2xl: 48px;
    
    /* Border Radius */
    --radius-sm: 4px;
    --radius-md: 8px;
    --radius-lg: 12px;
    --radius-full: 9999px;
    
    /* Typography */
    --font-primary: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-heading: 'Poppins', 'Inter', sans-serif;
}

/* Reset & Base Styles */
*,
*::before,
*::after {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: var(--font-primary);
    background-color: #000814;
    color: var(--white);
    line-height: 1.6;
    overflow-x: hidden;
}

.container {
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 var(--spacing-lg);
}

.container-header {
    max-width: 1400px;
    margin: 0 auto;
    padding: 0 var(--spacing-lg);
}

/* ========================================
   Header
   ======================================== */
.main-header {
    background-color: var(--primary-blue);
    position: sticky;
    top: 0;
    z-index: 1000;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
}

.container-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 64px;
}

.logo {
    display: flex;
    align-items: center;
    gap: var(--spacing-sm);
    font-family: var(--font-heading);
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--white);
}

.logo-icon {
    font-size: 1.5rem;
}

.main-nav {
    display: flex;
    gap: var(--spacing-xl);
}

.nav-link {
    color: rgba(255, 255, 255, 0.8);
    text-decoration: none;
    font-weight: 500;
    font-size: 0.95rem;
    transition: color 0.3s ease;
    position: relative;
}

.nav-link:hover,
.nav-link.active {
    color: var(--professional-cyan);
}

.nav-link.active::after {
    content: '';
    position: absolute;
    bottom: -20px;
    left: 0;
    right: 0;
    height: 3px;
    background-color: var(--professional-cyan);
}

.header-actions {
    display: flex;
    align-items: center;
    gap: var(--spacing-md);
}

.icon-btn {
    background: transparent;
    border: none;
    color: var(--white);
    font-size: 1.25rem;
    cursor: pointer;
    padding: var(--spacing-sm);
    border-radius: var(--radius-md);
    transition: background-color 0.3s ease;
}

.icon-btn:hover {
    background-color: rgba(255, 255, 255, 0.1);
}

.user-avatar {
    width: 36px;
    height: 36px;
    background: var(--professional-cyan);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    cursor: pointer;
}

/* ========================================
   Hero Section
   ======================================== */
.hero-section {
    background: var(--hero-gradient);
    padding: var(--spacing-2xl) 0 80px;
    text-align: center;
}

.hero-content {
    max-width: 900px;
    margin: 0 auto;
    padding: 0 var(--spacing-lg);
}

.hero-title {
    font-family: var(--font-heading);
    font-size: 3.5rem;
    font-weight: 700;
    margin-bottom: var(--spacing-md);
    background: linear-gradient(135deg, var(--white) 0%, var(--professional-cyan) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-tagline {
    font-size: 1.25rem;
    color: rgba(255, 255, 255, 0.9);
    margin-bottom: var(--spacing-2xl);
    font-weight: 400;
}

.hero-stats {
    display: flex;
    justify-content: center;
    gap: var(--spacing-2xl);
    margin-bottom: var(--spacing-2xl);
}

.stat-item {
    text-align: center;
}

.stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--professional-cyan);
    margin-bottom: var(--spacing-xs);
}

.stat-label {
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.7);
    text-transform: uppercase;
    letter-spacing: 1px;
}

.hero-cta {
    display: flex;
    gap: var(--spacing-md);
    justify-content: center;
}

/* ========================================
   Buttons
   ======================================== */
.btn {
    padding: 12px 28px;
    border-radius: var(--radius-md);
    font-weight: 600;
    font-size: 0.95rem;
    cursor: pointer;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    border: none;
    font-family: var(--font-primary);
}

.btn-primary {
    background-color: var(--professional-cyan);
    color: #000;
}

.btn-primary:hover {
    background-color: #00B8E6;
    transform: translateY(-2px);
    box-shadow: 0 8px 16px rgba(0, 212, 255, 0.3);
}

.btn-secondary {
    background-color: transparent;
    color: var(--professional-cyan);
    border: 2px solid var(--professional-cyan);
}

.btn-secondary:hover {
    background-color: var(--professional-cyan);
    color: #000;
}

.btn-outline {
    background-color: transparent;
    color: var(--professional-cyan);
    border: 2px solid var(--professional-cyan);
    padding: 10px 20px;
    font-size: 0.9rem;
}

.btn-outline:hover {
    background-color: var(--professional-cyan);
    color: #000;
}

.btn-view-report {
    width: 100%;
    padding: 12px;
    background: transparent;
    border: 2px solid var(--professional-cyan);
    color: var(--professional-cyan);
    font-weight: 600;
    border-radius: var(--radius-md);
    cursor: pointer;
    transition: all 0.3s ease;
    margin-top: var(--spacing-md);
}

.btn-view-report:hover {
    background-color: var(--professional-cyan);
    color: #000;
}

/* ========================================
   Dashboard KPI Section
   ======================================== */
.dashboard-section {
    padding: var(--spacing-2xl) 0;
    background-color: #000814;
}

.kpi-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--spacing-lg);
}

.kpi-card {
    background: var(--card-gradient);
    padding: var(--spacing-lg);
    border-radius: var(--radius-lg);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    display: flex;
    gap: var(--spacing-md);
}

.kpi-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 24px -4px rgba(0, 0, 0, 0.3);
}

.kpi-icon {
    font-size: 2.5rem;
}

.kpi-content {
    flex: 1;
}

.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--white);
    margin-bottom: var(--spacing-xs);
}

.kpi-label {
    font-size: 0.9rem;
    color: var(--muted-text);
    margin-bottom: var(--spacing-sm);
}

.kpi-trend {
    font-size: 0.85rem;
    font-weight: 600;
}

.kpi-trend.positive {
    color: var(--success);
}

.kpi-trend.negative {
    color: var(--critical);
}

.kpi-progress {
    background-color: rgba(255, 255, 255, 0.1);
    height: 8px;
    border-radius: var(--radius-full);
    overflow: hidden;
    margin-top: var(--spacing-sm);
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, var(--professional-cyan), var(--success));
    border-radius: var(--radius-full);
    transition: width 1s ease;
}

.score-indicator {
    margin-top: var(--spacing-sm);
}

.compliance-badge {
    display: inline-block;
    padding: 6px 12px;
    background-color: rgba(16, 185, 129, 0.2);
    color: var(--success);
    border-radius: var(--radius-md);
    font-size: 0.85rem;
    font-weight: 600;
    margin-top: var(--spacing-sm);
}

/* ========================================
   Reports Section
   ======================================== */
.reports-section {
    padding: var(--spacing-2xl) 0;
    background: linear-gradient(135deg, rgba(0, 45, 101, 0.3) 0%, rgba(0, 0, 0, 0.5) 50%, rgba(48, 0, 99, 0.3) 100%);
}

.section-title {
    font-family: var(--font-heading);
    font-size: 2.5rem;
    font-weight: 700;
    text-align: center;
    margin-bottom: var(--spacing-2xl);
    color: var(--white);
}

.reports-carousel {
    padding-bottom: 60px;
}

.report-card {
    background: var(--card-gradient);
    border-radius: var(--radius-lg);
    padding: var(--spacing-lg);
    height: 420px;
    border: 2px solid transparent;
    transition: all 0.3s ease;
    cursor: pointer;
    display: flex;
    flex-direction: column;
}

.report-card:hover {
    border-color: rgba(0, 212, 255, 0.5);
    transform: translateY(-4px);
    box-shadow: 0 12px 24px rgba(0, 212, 255, 0.2);
}

.report-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: var(--spacing-md);
}

.report-icon {
    font-size: 2rem;
}

.report-time {
    font-size: 0.85rem;
    color: var(--muted-text);
}

.report-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: var(--spacing-sm);
    color: var(--white);
}

.report-meta {
    display: flex;
    gap: var(--spacing-sm);
    color: var(--muted-text);
    font-size: 0.9rem;
    margin-bottom: var(--spacing-md);
}

.badge-group {
    display: flex;
    gap: var(--spacing-sm);
    margin-bottom: var(--spacing-md);
    flex-wrap: wrap;
}

.badge {
    padding: 6px 14px;
    border-radius: var(--radius-full);
    font-size: 0.85rem;
    font-weight: 600;
}

.badge-critical {
    background-color: rgba(220, 38, 38, 0.2);
    color: var(--critical);
    border: 1px solid var(--critical);
}

.badge-high {
    background-color: rgba(234, 88, 12, 0.2);
    color: var(--high);
    border: 1px solid var(--high);
}

.badge-medium {
    background-color: rgba(217, 119, 6, 0.2);
    color: var(--medium);
    border: 1px solid var(--medium);
}

.badge-low {
    background-color: rgba(5, 150, 105, 0.2);
    color: var(--low);
    border: 1px solid var(--low);
}

.badge-info {
    background-color: rgba(37, 99, 235, 0.2);
    color: var(--info);
    border: 1px solid var(--info);
}

.badge-success {
    background-color: rgba(16, 185, 129, 0.2);
    color: var(--success);
    border: 1px solid var(--success);
}

.badge-warning {
    background-color: rgba(217, 119, 6, 0.2);
    color: var(--medium);
    border: 1px solid var(--medium);
}

.report-score {
    margin-top: auto;
    padding-top: var(--spacing-md);
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.score-label {
    font-size: 0.85rem;
    color: var(--muted-text);
    margin-bottom: var(--spacing-xs);
}

.score-value {
    font-size: 2rem;
    font-weight: 700;
    color: var(--professional-cyan);
}

/* Swiper Customization */
.swiper-button-prev,
.swiper-button-next {
    color: var(--professional-cyan);
}

.swiper-pagination-bullet {
    background-color: var(--white);
}

.swiper-pagination-bullet-active {
    background-color: var(--professional-cyan);
}

/* ========================================
   Report Modal
   ======================================== */
.report-modal {
    display: none;
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 2000;
}

.report-modal.active {
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: rgba(0, 0, 0, 0.85);
}

.modal-content {
    position: relative;
    background: var(--card-gradient);
    max-width: 1200px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    border-radius: var(--radius-lg);
    box-shadow: 0 24px 48px rgba(0, 0, 0, 0.5);
    z-index: 1;
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-lg);
    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.modal-title {
    font-size: 1.75rem;
    font-weight: 600;
}

.modal-close {
    background: transparent;
    border: none;
    color: var(--white);
    font-size: 2rem;
    cursor: pointer;
    padding: 0;
    width: 40px;
    height: 40px;
    border-radius: var(--radius-md);
    transition: background-color 0.3s ease;
}

.modal-close:hover {
    background-color: rgba(255, 255, 255, 0.1);
}

.modal-body {
    padding: var(--spacing-lg);
}

.report-details-grid {
    display: grid;
    gap: var(--spacing-xl);
}

.detail-section {
    background-color: rgba(255, 255, 255, 0.05);
    padding: var(--spacing-lg);
    border-radius: var(--radius-md);
}

.detail-title {
    font-size: 1.5rem;
    margin-bottom: var(--spacing-md);
    color: var(--professional-cyan);
}

/* ========================================
   Features Section
   ======================================== */
.features-section {
    padding: var(--spacing-2xl) 0 80px;
    background-color: #000;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: var(--spacing-xl);
}

.feature-card {
    background: var(--card-gradient);
    padding: var(--spacing-xl);
    border-radius: var(--radius-lg);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    transition: all 0.3s ease;
    text-align: center;
}

.feature-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 12px 24px -4px rgba(0, 0, 0, 0.4);
}

.feature-icon {
    font-size: 3rem;
    margin-bottom: var(--spacing-md);
}

.feature-title {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: var(--spacing-md);
    color: var(--white);
}

.feature-description {
    color: var(--muted-text);
    margin-bottom: var(--spacing-md);
    line-height: 1.7;
}

.feature-metric {
    color: var(--professional-cyan);
    font-weight: 600;
    margin-bottom: var(--spacing-md);
}

/* ========================================
   Footer
   ======================================== */
.main-footer {
    background-color: #000;
    padding: var(--spacing-xl) 0;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.footer-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: var(--spacing-md);
}

.footer-content p {
    color: var(--muted-text);
    margin: 0;
}

.footer-links {
    display: flex;
    gap: var(--spacing-lg);
}

.footer-links a {
    color: var(--muted-text);
    text-decoration: none;
    transition: color 0.3s ease;
}

.footer-links a:hover {
    color: var(--professional-cyan);
}

/* ========================================
   Responsive Design
   ======================================== */
@media (max-width: 1024px) {
    .hero-title {
        font-size: 2.5rem;
    }
    
    .hero-stats {
        gap: var(--spacing-lg);
    }
    
    .stat-value {
        font-size: 1.5rem;
    }
}

@media (max-width: 768px) {
    .main-nav {
        display: none;
    }
    
    .hero-title {
        font-size: 2rem;
    }
    
    .hero-tagline {
        font-size: 1rem;
    }
    
    .hero-stats {
        flex-direction: column;
        gap: var(--spacing-md);
    }
    
    .hero-cta {
        flex-direction: column;
    }
    
    .kpi-grid {
        grid-template-columns: 1fr;
    }
    
    .section-title {
        font-size: 2rem;
    }
    
    .features-grid {
        grid-template-columns: 1fr;
    }
    
    .footer-content {
        flex-direction: column;
        text-align: center;
    }
}

/* ========================================
   Animations
   ======================================== */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(20px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.hero-content > * {
    animation: fadeIn 0.8s ease-out forwards;
}

/* Smooth scrolling */
html {
    scroll-behavior: smooth;
}'''

# Save CSS file
with open('home.css', 'w', encoding='utf-8') as f:
    f.write(css_content)

print("✅ home.css file created successfully!")
print(f"File size: {len(css_content)} characters")
