
# JavaScript Content
js_content = '''// ========================================
// NeuraShield.AI - Professional JavaScript
// ========================================

// Report Data
const reportsData = {
    1: {
        id: 1,
        title: "Flask Security Audit",
        timestamp: "Today, 3:30 PM",
        linesAnalyzed: 1247,
        filesScanned: 23,
        bugDetection: {
            bugsFound: 1,
            overallRisk: "HIGH",
            bugs: [
                {
                    title: "Insecure Default Configuration",
                    severity: "HIGH",
                    line: "app.py:15",
                    description: "Flask application running with debug=True in production environment. This exposes sensitive debugging information and can lead to remote code execution.",
                    cwe: "CWE-16",
                    cvssScore: 8.1,
                    fix: "Set app.debug=False for production deployment. Use a proper WSGI server like Gunicorn or uWSGI. Implement proper error handling without exposing stack traces."
                }
            ]
        },
        optimization: {
            timeComplexity: "O(1)",
            spaceComplexity: "O(1)",
            status: "well-optimized",
            optimizationsFound: 0,
            message: "Code is well-optimized with efficient time and space complexity."
        },
        securityScoring: {
            overallScore: 8.1,
            severity: "HIGH",
            riskSummary: "The application is currently running in a mode that is not suitable for production environments, potentially exposing it to various security threats. Immediate action is required.",
            vulnerabilities: [
                {
                    title: "Improper Configuration",
                    cvssScore: 8.1,
                    cvssVector: "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L",
                    cwe: "CWE-16",
                    remediation: "Ensure the application is configured for production use, including disabling debug mode, using secure configurations, and implementing proper access controls."
                }
            ],
            immediateActions: [
                "Disable debug mode and ensure the application is running in a production environment",
                "Review and implement secure configuration settings",
                "Conduct a security audit to identify and mitigate any other potential vulnerabilities"
            ]
        }
    },
    2: {
        id: 2,
        title: "API Security Review",
        timestamp: "Today, 2:15 PM",
        linesAnalyzed: 892,
        filesScanned: 15,
        bugDetection: {
            bugsFound: 0,
            overallRisk: "NONE",
            bugs: []
        },
        optimization: {
            timeComplexity: "O(1)",
            spaceComplexity: "O(1)",
            status: "well-optimized",
            optimizationsFound: 0,
            message: "No bugs detected. Code follows security best practices."
        },
        securityScoring: {
            overallScore: 9.2,
            severity: "LOW",
            riskSummary: "The application demonstrates excellent security practices with no critical vulnerabilities detected. Continue regular monitoring.",
            vulnerabilities: [],
            immediateActions: [
                "Continue regular security monitoring",
                "Maintain current security best practices",
                "Schedule periodic security audits"
            ]
        }
    },
    3: {
        id: 3,
        title: "E-commerce Backend",
        timestamp: "Today, 11:45 AM",
        linesAnalyzed: 2156,
        filesScanned: 45,
        bugDetection: {
            bugsFound: 3,
            overallRisk: "MEDIUM",
            bugs: [
                {
                    title: "SQL Injection Vulnerability",
                    severity: "MEDIUM",
                    line: "user_controller.py:89",
                    description: "User input is directly concatenated into SQL query without proper sanitization or parameterization.",
                    cwe: "CWE-89",
                    cvssScore: 6.5,
                    fix: "Use parameterized queries or ORM methods to prevent SQL injection. Never concatenate user input directly into SQL statements."
                },
                {
                    title: "Improper Input Validation",
                    severity: "MEDIUM",
                    line: "payment_handler.py:142",
                    description: "Payment amount validation is insufficient and could allow negative values or extremely large amounts.",
                    cwe: "CWE-20",
                    cvssScore: 5.8,
                    fix: "Implement comprehensive input validation including type checking, range validation, and business logic constraints."
                },
                {
                    title: "Information Disclosure",
                    severity: "MEDIUM",
                    line: "error_handler.py:23",
                    description: "Error messages expose internal system information including database structure and file paths.",
                    cwe: "CWE-200",
                    cvssScore: 5.3,
                    fix: "Implement generic error messages for users while logging detailed errors securely for administrators."
                }
            ]
        },
        optimization: {
            timeComplexity: "O(n²) for search operations",
            spaceComplexity: "O(n)",
            status: "needs-improvement",
            optimizationsFound: 2,
            suggestions: [
                {
                    type: "ALGORITHMIC",
                    improvement: "Replace nested loops in product search with hash-based lookup. This will reduce time complexity from O(n²) to O(n).",
                    tradeoffs: "Requires additional memory for hash table but significantly improves search performance."
                },
                {
                    type: "DATABASE",
                    improvement: "Add database indexes on frequently queried columns (user_id, order_date, product_sku).",
                    tradeoffs: "Slightly slower writes but much faster read operations for customer queries."
                }
            ]
        },
        securityScoring: {
            overallScore: 6.3,
            severity: "MEDIUM",
            riskSummary: "The application has medium-level vulnerabilities primarily due to improper input validation and potential information disclosure. These issues should be addressed promptly.",
            vulnerabilities: [
                {
                    title: "Improper Input Validation",
                    cvssScore: 6.3,
                    cvssVector: "CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N",
                    cwe: "CWE-20",
                    remediation: "Implement proper input validation and sanitization for all user inputs across the application."
                },
                {
                    title: "Information Disclosure",
                    cvssScore: 5.3,
                    cvssVector: "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N",
                    cwe: "CWE-200",
                    remediation: "Limit the exposure of internal data structures and ensure only necessary information is exposed to end users."
                }
            ],
            immediateActions: [
                "Implement input validation and sanitization for all endpoints",
                "Review and restrict data exposure to only what is necessary",
                "Add proper error handling to prevent information leakage",
                "Conduct code review for similar vulnerabilities in other modules"
            ]
        }
    }
};

// Initialize Swiper Carousel
const swiper = new Swiper('.reports-carousel', {
    slidesPerView: 1,
    spaceBetween: 20,
    loop: true,
    navigation: {
        nextEl: '.swiper-button-next',
        prevEl: '.swiper-button-prev',
    },
    pagination: {
        el: '.swiper-pagination',
        clickable: true,
    },
    breakpoints: {
        640: {
            slidesPerView: 1,
        },
        768: {
            slidesPerView: 2,
        },
        1024: {
            slidesPerView: 3,
        },
    },
});

// Modal Functionality
const modal = document.getElementById('reportModal');
const modalOverlay = modal.querySelector('.modal-overlay');
const modalClose = modal.querySelector('.modal-close');
const reportCards = document.querySelectorAll('.report-card');

// Open modal when clicking on report card or view button
reportCards.forEach(card => {
    card.addEventListener('click', function() {
        const reportId = parseInt(this.dataset.report);
        openReportModal(reportId);
    });
});

// Close modal handlers
modalClose.addEventListener('click', closeModal);
modalOverlay.addEventListener('click', closeModal);

// Close on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && modal.classList.contains('active')) {
        closeModal();
    }
});

function openReportModal(reportId) {
    const report = reportsData[reportId];
    if (!report) return;

    // Populate modal content
    populateBugDetection(report.bugDetection);
    populateOptimization(report.optimization);
    populateSecurity(report.securityScoring);

    // Show modal
    modal.classList.add('active');
    document.body.style.overflow = 'hidden';
}

function closeModal() {
    modal.classList.remove('active');
    document.body.style.overflow = 'auto';
}

function populateBugDetection(bugData) {
    const bugsList = document.getElementById('bugsList');
    
    if (bugData.bugsFound === 0) {
        bugsList.innerHTML = `
            <div style="text-align: center; padding: 2rem; color: #10B981;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">✓</div>
                <div style="font-size: 1.25rem; font-weight: 600;">No Bugs Detected</div>
                <div style="color: #64748B; margin-top: 0.5rem;">Your code is clean!</div>
            </div>
        `;
        return;
    }

    let html = `
        <div style="margin-bottom: 1.5rem;">
            <div style="font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem;">
                ⚠ Bugs Found: ${bugData.bugsFound}
            </div>
            <div style="color: #64748B;">Overall Risk: <span class="badge badge-${bugData.overallRisk.toLowerCase()}">${bugData.overallRisk}</span></div>
        </div>
    `;

    bugData.bugs.forEach((bug, index) => {
        html += `
            <div style="background: rgba(255,255,255,0.03); padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem; border-left: 4px solid var(--${bug.severity.toLowerCase()});">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                    <h4 style="margin: 0; font-size: 1.1rem;">${bug.title}</h4>
                    <span class="badge badge-${bug.severity.toLowerCase()}">${bug.severity}</span>
                </div>
                <div style="color: #64748B; margin-bottom: 0.75rem;">
                    <strong>Line:</strong> ${bug.line} | <strong>CWE:</strong> ${bug.cwe} | <strong>CVSS:</strong> ${bug.cvssScore}
                </div>
                <div style="margin-bottom: 1rem; line-height: 1.6;">
                    ${bug.description}
                </div>
                <div style="background: rgba(0,212,255,0.1); padding: 1rem; border-radius: 6px; border-left: 3px solid var(--professional-cyan);">
                    <strong style="color: var(--professional-cyan);">Fix:</strong><br>
                    <span style="color: #E2E8F0;">${bug.fix}</span>
                </div>
            </div>
        `;
    });

    bugsList.innerHTML = html;
}

function populateOptimization(optData) {
    const optContent = document.getElementById('optimizationContent');
    
    let html = `
        <div style="margin-bottom: 1.5rem;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                <div style="background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 8px;">
                    <div style="color: #64748B; font-size: 0.9rem; margin-bottom: 0.5rem;">Time Complexity</div>
                    <div style="font-size: 1.5rem; font-weight: 600; color: var(--professional-cyan);">${optData.timeComplexity}</div>
                </div>
                <div style="background: rgba(255,255,255,0.03); padding: 1rem; border-radius: 8px;">
                    <div style="color: #64748B; font-size: 0.9rem; margin-bottom: 0.5rem;">Space Complexity</div>
                    <div style="font-size: 1.5rem; font-weight: 600; color: var(--professional-cyan);">${optData.spaceComplexity}</div>
                </div>
            </div>
            <div style="text-align: center; padding: 1.5rem; background: rgba(255,255,255,0.03); border-radius: 8px;">
                <div style="font-size: 2rem; margin-bottom: 0.5rem;">
                    ${optData.status === 'well-optimized' ? '✓' : '⚡'}
                </div>
                <div style="font-size: 1.1rem; font-weight: 600; color: ${optData.status === 'well-optimized' ? '#10B981' : '#D97706'};">
                    ${optData.status === 'well-optimized' ? 'Well Optimized' : 'Needs Improvement'}
                </div>
            </div>
        </div>
    `;

    if (optData.optimizationsFound > 0 && optData.suggestions) {
        html += '<div style="margin-top: 1.5rem;"><h4 style="margin-bottom: 1rem;">⚡ Optimization Suggestions</h4>';
        optData.suggestions.forEach((suggestion, index) => {
            html += `
                <div style="background: rgba(255,255,255,0.03); padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;">
                    <div style="color: var(--professional-cyan); font-weight: 600; margin-bottom: 0.5rem;">
                        ${suggestion.type}
                    </div>
                    <div style="margin-bottom: 1rem; line-height: 1.6;">
                        ${suggestion.improvement}
                    </div>
                    <div style="color: #64748B; font-size: 0.9rem;">
                        <strong>Tradeoffs:</strong> ${suggestion.tradeoffs}
                    </div>
                </div>
            `;
        });
        html += '</div>';
    } else {
        html += `<div style="color: #64748B; margin-top: 1rem;">${optData.message}</div>`;
    }

    optContent.innerHTML = html;
}

function populateSecurity(secData) {
    const secContent = document.getElementById('securityContent');
    
    // Determine score color
    let scoreColor = '#10B981'; // Low
    if (secData.overallScore >= 9.0) scoreColor = '#DC2626'; // Critical
    else if (secData.overallScore >= 7.0) scoreColor = '#EA580C'; // High
    else if (secData.overallScore >= 4.0) scoreColor = '#D97706'; // Medium

    let html = `
        <div style="text-align: center; margin-bottom: 2rem;">
            <div style="font-size: 4rem; font-weight: 700; color: ${scoreColor}; margin-bottom: 0.5rem;">
                ${secData.overallScore}/10
            </div>
            <div style="font-size: 1.1rem; margin-bottom: 0.5rem;">
                <span class="badge badge-${secData.severity.toLowerCase()}">${secData.severity} Severity</span>
            </div>
        </div>

        <div style="background: rgba(255,255,255,0.03); padding: 1.5rem; border-radius: 8px; margin-bottom: 1.5rem;">
            <h4 style="margin-bottom: 1rem;">Risk Summary</h4>
            <p style="color: #E2E8F0; line-height: 1.7;">${secData.riskSummary}</p>
        </div>
    `;

    if (secData.vulnerabilities.length > 0) {
        html += '<h4 style="margin-bottom: 1rem;">🛡 Vulnerabilities</h4>';
        secData.vulnerabilities.forEach((vuln, index) => {
            html += `
                <div style="background: rgba(255,255,255,0.03); padding: 1.5rem; border-radius: 8px; margin-bottom: 1rem;">
                    <h5 style="margin-bottom: 0.75rem;">${vuln.title}</h5>
                    <div style="color: #64748B; margin-bottom: 1rem;">
                        <strong>CVSS Score:</strong> ${vuln.cvssScore} | 
                        <strong>Vector:</strong> ${vuln.cvssVector} | 
                        <strong>CWE:</strong> ${vuln.cwe}
                    </div>
                    <div style="background: rgba(0,212,255,0.1); padding: 1rem; border-radius: 6px;">
                        <strong style="color: var(--professional-cyan);">Remediation:</strong><br>
                        <span style="color: #E2E8F0;">${vuln.remediation}</span>
                    </div>
                </div>
            `;
        });
    }

    if (secData.immediateActions.length > 0) {
        html += `
            <div style="background: rgba(220,38,38,0.1); padding: 1.5rem; border-radius: 8px; margin-top: 1.5rem; border-left: 4px solid var(--critical);">
                <h4 style="color: var(--critical); margin-bottom: 1rem;">⚠ Immediate Actions Required</h4>
                <ul style="margin: 0; padding-left: 1.5rem; color: #E2E8F0;">
        `;
        secData.immediateActions.forEach(action => {
            html += `<li style="margin-bottom: 0.5rem;">${action}</li>`;
        });
        html += `
                </ul>
            </div>
        `;
    }

    secContent.innerHTML = html;
}

// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Update active nav link on scroll
window.addEventListener('scroll', () => {
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.nav-link');
    
    let current = '';
    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.clientHeight;
        if (window.pageYOffset >= sectionTop - 100) {
            current = section.getAttribute('id');
        }
    });

    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${current}`) {
            link.classList.add('active');
        }
    });
});

// Console log for developers
console.log('%c🛡️ NeuraShield.AI', 'color: #00D4FF; font-size: 24px; font-weight: bold;');
console.log('%cEnterprise-Grade Code Security Platform', 'color: #64748B; font-size: 14px;');
console.log('%cVersion: 2.1.0', 'color: #10B981; font-size: 12px;');'''

# Save JavaScript file
with open('home.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print("✅ home.js file created successfully!")
print(f"File size: {len(js_content)} characters")
print("\n" + "="*50)
print("ALL FILES CREATED SUCCESSFULLY!")
print("="*50)
print("\n📁 Files Generated:")
print("  ✓ home.html")
print("  ✓ home.css")
print("  ✓ home.js")
print("\n🚀 To run the website:")
print("  1. Place all three files in the same folder")
print("  2. Open home.html in your web browser")
print("  3. Enjoy your professional NeuraShield.AI dashboard!")
print("\n💡 Features:")
print("  • Professional enterprise design")
print("  • Responsive layout (mobile, tablet, desktop)")
print("  • Interactive Swiper carousel")
print("  • Detailed report modals")
print("  • Smooth animations and transitions")
print("  • Complete functionality with sample data")
