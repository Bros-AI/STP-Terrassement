document.addEventListener('DOMContentLoaded', () => {
    
    // ========================================
    // MOBILE MENU TOGGLE
    // ========================================
    const mobileBtn = document.querySelector('.mobile-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    const navLinks = document.querySelectorAll('.mobile-menu a');

    if (mobileBtn && mobileMenu) {
        mobileBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('active');
            const icon = mobileBtn.querySelector('i');
            
            if (mobileMenu.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-xmark');
                document.body.style.overflow = 'hidden';
            } else {
                icon.classList.remove('fa-xmark');
                icon.classList.add('fa-bars');
                document.body.style.overflow = '';
            }
        });

        // Close mobile menu when clicking a link
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                mobileMenu.classList.remove('active');
                const icon = mobileBtn.querySelector('i');
                icon.classList.remove('fa-xmark');
                icon.classList.add('fa-bars');
                document.body.style.overflow = '';
            });
        });

        // Close mobile menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!mobileBtn.contains(e.target) && !mobileMenu.contains(e.target)) {
                mobileMenu.classList.remove('active');
                const icon = mobileBtn.querySelector('i');
                icon.classList.remove('fa-xmark');
                icon.classList.add('fa-bars');
                document.body.style.overflow = '';
            }
        });
    }

    // ========================================
    // NAVBAR SCROLL EFFECT (OPTIMIZED)
    // ========================================
    const navbar = document.getElementById('navbar');
    let lastScroll = 0;
    let ticking = false;

    const updateNavbar = () => {
        const currentScroll = window.pageYOffset;

        if (currentScroll > 50) {
            navbar.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
            navbar.style.padding = '10px 0';
        } else {
            navbar.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
            navbar.style.padding = '15px 0';
        }

        lastScroll = currentScroll;
        ticking = false;
    };

    if (navbar) {
        window.addEventListener('scroll', () => {
            if (!ticking) {
                window.requestAnimationFrame(updateNavbar);
                ticking = true;
            }
        }, { passive: true });
    }

    // ========================================
    // SMOOTH SCROLLING FOR ANCHOR LINKS
    // ========================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            
            if (targetId === '#') {
                e.preventDefault();
                return;
            }
            
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                e.preventDefault();
                
                const headerOffset = 80;
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: "smooth"
                });
            }
        });
    });

    // ========================================
    // FAQ ACCORDION FUNCTIONALITY - ENHANCED
    // ========================================
    const faqItems = document.querySelectorAll('details');
    
    if (faqItems.length > 0) {
        // Add CSS for smooth transitions
        const style = document.createElement('style');
        style.textContent = `
            details summary {
                cursor: pointer;
                transition: all 0.3s ease;
                user-select: none;
                list-style: none;
            }
            details summary::-webkit-details-marker {
                display: none;
            }
            details summary:hover {
                background: rgba(255, 180, 0, 0.1) !important;
                padding-left: 35px !important;
            }
            details[open] summary {
                background: rgba(255, 180, 0, 0.15) !important;
                color: var(--primary) !important;
                padding-left: 35px !important;
                border-bottom: 2px solid var(--primary);
            }
            details summary i {
                transition: transform 0.3s ease;
            }
            details[open] > summary::after {
                content: '';
                position: absolute;
                left: 0;
                right: 0;
                bottom: -2px;
                height: 2px;
                background: var(--primary);
            }
        `;
        document.head.appendChild(style);

        faqItems.forEach((item, index) => {
            const summary = item.querySelector('summary');
            
            if (summary) {
                // Make summary position relative for after pseudo-element
                summary.style.position = 'relative';
                
                // Add click animation
                summary.addEventListener('click', (e) => {
                    // Optional: Close other FAQ items (accordion behavior)
                    // Uncomment below for one-at-a-time behavior
                    /*
                    faqItems.forEach((otherItem, otherIndex) => {
                        if (otherIndex !== index && otherItem.open) {
                            otherItem.open = false;
                        }
                    });
                    */
                    
                    // Visual feedback on click
                    summary.style.transform = 'scale(0.98)';
                    setTimeout(() => {
                        summary.style.transform = 'scale(1)';
                    }, 150);
                });
                
                // Handle open/close state with icon rotation
                item.addEventListener('toggle', () => {
                    const icon = summary.querySelector('i');
                    
                    if (item.open) {
                        // Smooth scroll to element after opening
                        setTimeout(() => {
                            const yOffset = -100;
                            const element = item;
                            const y = element.getBoundingClientRect().top + window.pageYOffset + yOffset;
                            
                            window.scrollTo({ top: y, behavior: 'smooth' });
                        }, 100);
                        
                        // Add open animation to content
                        const content = item.querySelector('p');
                        if (content) {
                            content.style.animation = 'fadeInDown 0.3s ease';
                        }
                    }
                });
                
                // Add keyboard accessibility
                summary.addEventListener('keydown', (e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        summary.click();
                    }
                });
            }
        });
        
        // Add animation keyframes
        if (!document.getElementById('faq-animations')) {
            const animStyle = document.createElement('style');
            animStyle.id = 'faq-animations';
            animStyle.textContent = `
                @keyframes fadeInDown {
                    from {
                        opacity: 0;
                        transform: translateY(-10px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
            `;
            document.head.appendChild(animStyle);
        }
    }

    // ========================================
    // FORM HANDLING WITH VALIDATION
    // ========================================
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            const formData = new FormData(form);
            const btn = form.querySelector('button[type="submit"]');
            const originalText = btn.innerHTML;
            
            // Basic validation
            const inputs = form.querySelectorAll('input[required], select[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    isValid = false;
                    input.style.borderColor = '#ef4444';
                    
                    setTimeout(() => {
                        input.style.borderColor = '#e5e7eb';
                    }, 2000);
                }
            });
            
            if (!isValid) {
                showNotification('Veuillez remplir tous les champs obligatoires', 'error');
                return;
            }
            
            // Phone validation
            const phoneInput = form.querySelector('input[type="tel"]');
            if (phoneInput && phoneInput.value) {
                const phoneRegex = /^[0-9]{10}$/;
                if (!phoneRegex.test(phoneInput.value.replace(/\s/g, ''))) {
                    showNotification('Numéro de téléphone invalide (10 chiffres requis)', 'error');
                    phoneInput.style.borderColor = '#ef4444';
                    setTimeout(() => {
                        phoneInput.style.borderColor = '#e5e7eb';
                    }, 2000);
                    return;
                }
            }
            
            // Email validation
            const emailInput = form.querySelector('input[type="email"]');
            if (emailInput && emailInput.value) {
                const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
                if (!emailRegex.test(emailInput.value)) {
                    showNotification('Adresse email invalide', 'error');
                    emailInput.style.borderColor = '#ef4444';
                    setTimeout(() => {
                        emailInput.style.borderColor = '#e5e7eb';
                    }, 2000);
                    return;
                }
            }
            
            // Simulate form submission
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Envoi en cours...';
            btn.disabled = true;
            btn.style.opacity = '0.7';
            
            // Simulate API call
            setTimeout(() => {
                showNotification('Demande envoyée avec succès ! Nous vous contacterons sous 24h.', 'success');
                form.reset();
                btn.innerHTML = originalText;
                btn.disabled = false;
                btn.style.opacity = '1';
                
                // Optional: Track conversion
                if (typeof gtag !== 'undefined') {
                    gtag('event', 'conversion', {
                        'send_to': 'AW-CONVERSION_ID/CONVERSION_LABEL'
                    });
                }
            }, 1500);
        });
        
        // Real-time validation on input
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('input', () => {
                if (input.value.trim()) {
                    input.style.borderColor = '#10b981';
                } else if (input.hasAttribute('required')) {
                    input.style.borderColor = '#e5e7eb';
                }
            });
        });
    });

    // ========================================
    // NOTIFICATION SYSTEM
    // ========================================
    function showNotification(message, type = 'success') {
        const existingNotif = document.querySelector('.notification');
        if (existingNotif) {
            existingNotif.remove();
        }
        
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fa-solid ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            <span>${message}</span>
        `;
        
        Object.assign(notification.style, {
            position: 'fixed',
            top: '100px',
            right: '20px',
            background: type === 'success' ? '#10b981' : '#ef4444',
            color: 'white',
            padding: '16px 24px',
            borderRadius: '10px',
            boxShadow: '0 10px 25px rgba(0,0,0,0.2)',
            zIndex: '9999',
            display: 'flex',
            alignItems: 'center',
            gap: '12px',
            fontSize: '0.95rem',
            fontWeight: '600',
            animation: 'slideInRight 0.4s ease',
            maxWidth: '400px'
        });
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.4s ease';
            setTimeout(() => {
                notification.remove();
            }, 400);
        }, 5000);
    }
    
    // Add animation keyframes
    if (!document.getElementById('notification-animations')) {
        const style = document.createElement('style');
        style.id = 'notification-animations';
        style.textContent = `
            @keyframes slideInRight {
                from {
                    transform: translateX(400px);
                    opacity: 0;
                }
                to {
                    transform: translateX(0);
                    opacity: 1;
                }
            }
            @keyframes slideOutRight {
                from {
                    transform: translateX(0);
                    opacity: 1;
                }
                to {
                    transform: translateX(400px);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }

    // ========================================
    // SCROLL REVEAL ANIMATIONS
    // ========================================
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    const animatedElements = document.querySelectorAll('.card, .problem-card, .process-step, .testimonial-card, .gallery-item, .why-card');
    
    animatedElements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        el.style.transitionDelay = `${index * 0.1}s`;
        observer.observe(el);
    });

    // ========================================
    // ACTIVE NAV LINK ON SCROLL
    // ========================================
    const sections = document.querySelectorAll('section[id]');
    const navItems = document.querySelectorAll('.nav-links a');
    let navTicking = false;

    const updateActiveNav = () => {
        let current = '';
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            
            if (pageYOffset >= (sectionTop - 100)) {
                current = section.getAttribute('id');
            }
        });

        navItems.forEach(item => {
            item.classList.remove('active');
            if (item.getAttribute('href') === `#${current}`) {
                item.classList.add('active');
            }
        });

        navTicking = false;
    };

    if (sections.length > 0) {
        window.addEventListener('scroll', () => {
            if (!navTicking) {
                window.requestAnimationFrame(updateActiveNav);
                navTicking = true;
            }
        }, { passive: true });
    }

    // Add active link styles
    if (!document.getElementById('active-nav-styles')) {
        const activeStyle = document.createElement('style');
        activeStyle.id = 'active-nav-styles';
        activeStyle.textContent = `
            .nav-links a.active {
                color: #FFB400;
                position: relative;
            }
            .nav-links a.active::after {
                content: '';
                position: absolute;
                bottom: -5px;
                left: 0;
                right: 0;
                height: 2px;
                background: #FFB400;
            }
        `;
        document.head.appendChild(activeStyle);
    }

    // ========================================
    // GALLERY LIGHTBOX
    // ========================================
    const galleryItems = document.querySelectorAll('.gallery-item');
    
    galleryItems.forEach(item => {
        item.addEventListener('click', () => {
            const img = item.querySelector('img');
            const caption = item.querySelector('.gallery-caption');
            
            if (!img) return;
            
            const lightbox = document.createElement('div');
            lightbox.className = 'lightbox';
            lightbox.innerHTML = `
                <div class="lightbox-content">
                    <span class="lightbox-close" aria-label="Fermer">&times;</span>
                    <img src="${img.src}" alt="${img.alt}" loading="lazy">
                    ${caption ? `<div class="lightbox-caption">${caption.innerHTML}</div>` : ''}
                </div>
            `;
            
            Object.assign(lightbox.style, {
                position: 'fixed',
                top: '0',
                left: '0',
                width: '100%',
                height: '100%',
                background: 'rgba(0,0,0,0.95)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: '10000',
                animation: 'fadeIn 0.3s ease'
            });
            
            document.body.appendChild(lightbox);
            document.body.style.overflow = 'hidden';
            
            const closeBtn = lightbox.querySelector('.lightbox-close');
            closeBtn.addEventListener('click', () => {
                closeLightbox(lightbox);
            });
            
            lightbox.addEventListener('click', (e) => {
                if (e.target === lightbox) {
                    closeLightbox(lightbox);
                }
            });

            const escHandler = (e) => {
                if (e.key === 'Escape') {
                    closeLightbox(lightbox);
                    document.removeEventListener('keydown', escHandler);
                }
            };
            document.addEventListener('keydown', escHandler);
        });
    });

    function closeLightbox(lightbox) {
        lightbox.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => {
            lightbox.remove();
            document.body.style.overflow = '';
        }, 300);
    }

    // Lightbox styles
    if (!document.getElementById('lightbox-styles')) {
        const lightboxStyle = document.createElement('style');
        lightboxStyle.id = 'lightbox-styles';
        lightboxStyle.textContent = `
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            @keyframes fadeOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }
            .lightbox-content {
                position: relative;
                max-width: 90%;
                max-height: 90vh;
                animation: zoomIn 0.3s ease;
            }
            @keyframes zoomIn {
                from { transform: scale(0.8); opacity: 0; }
                to { transform: scale(1); opacity: 1; }
            }
            .lightbox-content img {
                max-width: 100%;
                max-height: 80vh;
                border-radius: 10px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.5);
            }
            .lightbox-close {
                position: absolute;
                top: -40px;
                right: 0;
                color: white;
                font-size: 40px;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .lightbox-close:hover {
                color: #FFB400;
                transform: rotate(90deg);
            }
            .lightbox-caption {
                color: white;
                text-align: center;
                margin-top: 20px;
                font-size: 1.1rem;
            }
        `;
        document.head.appendChild(lightboxStyle);
    }

    // ========================================
    // COUNTER ANIMATION FOR STATS
    // ========================================
    const stats = document.querySelectorAll('.stat-number, .stat strong');
    
    const animateCounter = (element) => {
        const target = element.textContent.trim();
        const isPercentage = target.includes('%');
        const hasPlus = target.includes('+');
        const hasDivider = target.includes('/');
        
        let number = parseFloat(target.replace(/[^\d.]/g, ''));
        
        if (isNaN(number)) return;
        
        let current = 0;
        const increment = number / 50;
        const duration = 1500;
        const stepTime = duration / 50;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= number) {
                element.textContent = number + (hasDivider ? '/5' : '') + (isPercentage ? '%' : '') + (hasPlus ? '+' : '');
                clearInterval(timer);
            } else {
                let displayValue = hasDivider && number < 5 ? current.toFixed(1) : Math.floor(current);
                element.textContent = displayValue + (hasDivider ? '/5' : '') + (isPercentage ? '%' : '') + (hasPlus ? '+' : '');
            }
        }, stepTime);
    };

    const statsObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                statsObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    stats.forEach(stat => statsObserver.observe(stat));

    // ========================================
    // LAZY LOADING FOR IMAGES
    // ========================================
    if ('loading' in HTMLImageElement.prototype) {
        const images = document.querySelectorAll('img[loading="lazy"]');
        images.forEach(img => {
            img.src = img.src;
        });
    } else {
        const lazyImages = document.querySelectorAll('img[loading="lazy"]');
        
        const imageObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src || img.src;
                    img.classList.add('loaded');
                    imageObserver.unobserve(img);
                }
            });
        });

        lazyImages.forEach(img => imageObserver.observe(img));
    }

    // ========================================
    // PHONE NUMBER FORMATTING
    // ========================================
    const phoneInputs = document.querySelectorAll('input[type="tel"]');
    phoneInputs.forEach(input => {
        input.addEventListener('input', (e) => {
            let value = e.target.value.replace(/\D/g, '');
            if (value.length > 10) {
                value = value.slice(0, 10);
            }
            e.target.value = value;
        });
    });

    // ========================================
    // WHATSAPP BUTTON PULSE ANIMATION
    // ========================================
    const waButton = document.querySelector('.float-wa');
    if (waButton) {
        setInterval(() => {
            waButton.style.transform = 'scale(1.1)';
            setTimeout(() => {
                waButton.style.transform = 'scale(1)';
            }, 200);
        }, 3000);
    }

    // ========================================
    // PERFORMANCE MONITORING
    // ========================================
    if (window.performance && window.performance.timing) {
        window.addEventListener('load', () => {
            setTimeout(() => {
                const perfData = window.performance.timing;
                const pageLoadTime = perfData.loadEventEnd - perfData.navigationStart;
                const connectTime = perfData.responseEnd - perfData.requestStart;
                const renderTime = perfData.domComplete - perfData.domLoading;
                
                console.log('%c⚡ Performance Metrics:', 'font-weight: bold; color: #FFB400;');
                console.log(`Page Load Time: ${pageLoadTime}ms`);
                console.log(`Connect Time: ${connectTime}ms`);
                console.log(`Render Time: ${renderTime}ms`);
            }, 0);
        });
    }

    // ========================================
    // CONSOLE EASTER EGG
    // ========================================
    console.log('%cSTP TERRASSEMENT', 'font-size: 24px; font-weight: bold; color: #FFB400;');
    console.log('%cVous cherchez à améliorer votre site ? Contactez-nous !', 'font-size: 14px; color: #666;');
    console.log('%c📞 07 45 14 20 49', 'font-size: 16px; color: #25D366; font-weight: bold;');

});