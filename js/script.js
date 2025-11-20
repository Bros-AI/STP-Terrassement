document.addEventListener('DOMContentLoaded', () => {
    
    // Mobile Menu Toggle
    const mobileBtn = document.querySelector('.mobile-toggle');
    const mobileMenu = document.querySelector('.mobile-menu');
    const navLinks = document.querySelectorAll('.mobile-menu a');

    if (mobileBtn) {
        mobileBtn.addEventListener('click', () => {
            mobileMenu.classList.toggle('active');
            const icon = mobileBtn.querySelector('i');
            if (mobileMenu.classList.contains('active')) {
                icon.classList.remove('fa-bars');
                icon.classList.add('fa-xmark');
            } else {
                icon.classList.remove('fa-xmark');
                icon.classList.add('fa-bars');
            }
        });
    }

    // Close mobile menu when clicking a link
    navLinks.forEach(link => {
        link.addEventListener('click', () => {
            mobileMenu.classList.remove('active');
            const icon = mobileBtn.querySelector('i');
            icon.classList.remove('fa-xmark');
            icon.classList.add('fa-bars');
        });
    });

    // Navbar Scroll Effect (Shadow/Shrink)
    const navbar = document.getElementById('navbar');
    window.addEventListener('scroll', () => {
        if (window.scrollY > 50) {
            navbar.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.1)';
            navbar.style.padding = '10px 0';
        } else {
            navbar.style.boxShadow = 'none';
            navbar.style.padding = '15px 0';
        }
    });

    // Smooth Scrolling for Anchor Links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                const headerOffset = 80; // Height of fixed header
                const elementPosition = targetElement.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: "smooth"
                });
            }
        });
    });

    // Simple Form Validation (Visual feedback only)
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const btn = form.querySelector('button');
            const originalText = btn.innerText;
            
            // Simulate sending
            btn.innerText = 'Envoi...';
            btn.style.opacity = '0.7';
            
            setTimeout(() => {
                alert('Merci ! Votre demande a été reçue. Nous vous rappellerons au 07 45 14 20 49.');
                form.reset();
                btn.innerText = originalText;
                btn.style.opacity = '1';
            }, 1500);
        });
    });
});