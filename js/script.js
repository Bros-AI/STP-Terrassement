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
                document.body.style.overflow = 'hidden'; // Prevent scrolling when menu is open
            } else {
                icon.classList.remove('fa-xmark');
                icon.classList.add('fa-bars');
                document.body.style.overflow = ''; // Restore scrolling
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

    // PERFORMANCE: Use requestAnimationFrame for smooth scrolling
    const updateNavbar = () => {
        const currentScroll = window.pageYOffset;

        // Add shadow and shrink padding when scrolled
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

    window.addEventListener('scroll', () => {
        if (!ticking) {
            window.requestAnimationFrame(updateNavbar);
            ticking = true;
        }
    }, { passive: true }); // PERFORMANCE: Passive listener

    // ========================================
    // SMOOTH SCROLLING FOR ANCHOR LINKS
    // ========================================
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const targetId = this.getAttribute('href');
            
            // Skip if it's just a hash (#)
            if (targetId === '#') {
                e.preventDefault();
                return;
            }
            
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                e.preventDefault();
                
                const headerOffset = 80; // Height of fixed navbar
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
    // FORM HANDLING WITH VALIDATION
    // ========================================
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            
            // Get form data
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
                    
                    // Reset border color after 2 seconds
                    setTimeout(() => {
                        input.style.borderColor = '#e5e7eb';
                    }, 2000);
                }
            });
            
            if (!isValid) {
                // Show error message
                showNotification('Veuillez remplir tous les champs obligatoires', 'error');
                return;
            }
            
            // Simulate form submission
            btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Envoi en cours...';
            btn.disabled = true;
            btn.style.opacity = '0.7';
            
            // Simulate API call
            setTimeout(() => {
                // Success
                showNotification('Demande envoyée avec succès ! Nous vous contacterons sous 24h.', 'success');
                form.reset();
                btn.innerHTML = originalText;
                btn.disabled = false;
                btn.style.opacity = '1';
                
                // Optional: Redirect to WhatsApp after form submission
                // setTimeout(() => {
                //     window.open('https://wa.me/33745142049?text=Bonjour, je viens de remplir le formulaire sur votre site.', '_blank');
                // }, 2000);
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
        // Remove existing notification if any
        const existingNotif = document.querySelector('.notification');
        if (existingNotif) {
            existingNotif.remove();
        }
        
        // Create notification
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fa-solid ${type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle'}"></i>
            <span>${message}</span>
        `;
        
        // Add styles
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
        
        // Remove after 5 seconds
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
    // SCROLL REVEAL ANIMATIONS (OPTIMIZED WITH INTERSECTION OBSERVER)
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
                observer.unobserve(entry.target); // Stop observing after animation
            }
        });
    }, observerOptions);

    // Elements to animate on scroll
    const animatedElements = document.querySelectorAll('.card, .problem-card, .process-step, .testimonial-card, .gallery-item');
    
    animatedElements.forEach((el, index) => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        el.style.transitionDelay = `${index * 0.1}s`;
        observer.observe(el);
    });

    // ========================================
    // ACTIVE NAV LINK ON SCROLL (OPTIMIZED)
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

    window.addEventListener('scroll', () => {
        if (!navTicking) {
            window.requestAnimationFrame(updateActiveNav);
            navTicking = true;
        }
    }, { passive: true }); // PERFORMANCE: Passive listener

    // Add active link styles (only if not already added)
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
    // GALLERY LIGHTBOX (OPTIMIZED)
    // ========================================
    const galleryItems = document.querySelectorAll('.gallery-item');
    
    galleryItems.forEach(item => {
        item.addEventListener('click', () => {
            const img = item.querySelector('img');
            const caption = item.querySelector('.gallery-caption').innerHTML;
            
            // Create lightbox
            const lightbox = document.createElement('div');
            lightbox.className = 'lightbox';
            lightbox.innerHTML = `
                <div class="lightbox-content">
                    <span class="lightbox-close" aria-label="Fermer">&times;</span>
                    <img src="${img.src}" alt="${img.alt}" loading="lazy">
                    <div class="lightbox-caption">${caption}</div>
                </div>
            `;
            
            // Lightbox styles
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
            
            // Close lightbox
            const closeBtn = lightbox.querySelector('.lightbox-close');
            closeBtn.addEventListener('click', () => {
                closeLightbox(lightbox);
            });
            
            // Close on background click
            lightbox.addEventListener('click', (e) => {
                if (e.target === lightbox) {
                    closeLightbox(lightbox);
                }
            });

            // Close on ESC key
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

    // Lightbox styles (only if not already added)
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
    // COUNTER ANIMATION FOR STATS (OPTIMIZED)
    // ========================================
    const stats = document.querySelectorAll('.stat strong');
    
    const animateCounter = (element) => {
        const target = element.textContent;
        const isPercentage = target.includes('%');
        const hasPlus = target.includes('+');
        const number = parseInt(target);
        
        if (isNaN(number)) return;
        
        let current = 0;
        const increment = number / 50;
        const duration = 1500; // 1.5 seconds
        const stepTime = duration / 50;
        
        const timer = setInterval(() => {
            current += increment;
            if (current >= number) {
                element.textContent = number + (isPercentage ? '%' : '') + (hasPlus ? '+' : '');
                clearInterval(timer);
            } else {
                element.textContent = Math.floor(current) + (isPercentage ? '%' : '') + (hasPlus ? '+' : '');
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
    // LAZY LOADING FOR IMAGES (NATIVE + FALLBACK)
    // ========================================
    // Modern browsers support native lazy loading via loading="lazy"
    // This is a fallback for older browsers
    if ('loading' in HTMLImageElement.prototype) {
        // Browser supports native lazy loading
        const images = document.querySelectorAll('img[loading="lazy"]');
        images.forEach(img => {
            img.src = img.src; // Trigger loading
        });
    } else {
        // Fallback to Intersection Observer for older browsers
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
    // PERFORMANCE: DEBOUNCE UTILITY
    // ========================================
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    // ========================================
    // CONSOLE EASTER EGG
    // ========================================
    console.log('%cSTP TERRASSEMENT', 'font-size: 24px; font-weight: bold; color: #FFB400;');
    console.log('%cVous cherchez à améliorer votre site ? Contactez-nous !', 'font-size: 14px; color: #666;');
    console.log('%c📞 07 45 14 20 49', 'font-size: 16px; color: #25D366; font-weight: bold;');

    // ========================================
    // PERFORMANCE MONITORING (OPTIONAL - REMOVE IN PRODUCTION)
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

});