// Fade-in effect for sections
// This script will animate elements with the 'fade-in' class

document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('.fade-in').forEach(function(el, i) {
        setTimeout(() => {
            el.style.opacity = 1;
            el.style.transform = "none";
        }, 200 + i * 200);
    });

    // Custom confirmation modal logic
    const modal = document.getElementById('custom-confirm-modal');
    const yesBtn = document.getElementById('confirm-yes-btn');
    const noBtn = document.getElementById('confirm-no-btn');
    let formToSubmit = null;

    document.querySelectorAll('.delete-form').forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            formToSubmit = this;
            modal.style.display = 'flex';
        });
    });

    if (modal) {
        noBtn.addEventListener('click', () => {
            modal.style.display = 'none';
            formToSubmit = null;
        });

        yesBtn.addEventListener('click', () => {
            if (formToSubmit) {
                formToSubmit.submit();
            }
            modal.style.display = 'none';
        });

        // Also close modal if clicking on the overlay
        modal.addEventListener('click', function(e) {
            if (e.target === this) {
                modal.style.display = 'none';
                formToSubmit = null;
            }
        });
    }

    // Logic for 'x' button on file removal in edit forms
    document.querySelectorAll('.remove-file-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const target = this.dataset.target; // 'image' or 'attachment'
            const container = document.getElementById(`current-${target}-container`);
            const checkbox = document.getElementById(`remove_${target}_checkbox`);
            if (container) {
                container.style.display = 'none';
            }
            if (checkbox) {
                checkbox.checked = true;
            }
        });
    });

    // Notice Board Filtering
    const filterContainer = document.querySelector('.notice-filter-nav');
    if (filterContainer) {
        const filterButtons = filterContainer.querySelectorAll('.filter-btn');
        const noticeCards = document.querySelectorAll('.notice-grid .notice-card');

        filterButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Update active button state
                filterButtons.forEach(btn => btn.classList.remove('active'));
                this.classList.add('active');

                const filterValue = this.getAttribute('data-filter');

                // Filter cards
                noticeCards.forEach(card => {
                    const cardCategory = card.getAttribute('data-category');
                    if (filterValue === 'all' || filterValue === cardCategory) {
                        card.style.display = ''; // Or 'block', 'flex', etc., depending on your layout
                        card.classList.remove('hidden');

                    } else {
                        card.style.display = 'none';
                        card.classList.add('hidden');
                    }
                });
            });
        });
    }

    // Smooth scroll for map button
    const mapBtn = document.querySelector('a[href="#map-section"]');
    if (mapBtn) {
        mapBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const mapSection = document.getElementById('map-section');
            if (mapSection) {
                mapSection.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    }

    // Fade-in on scroll for cards (existing)
    const cards = document.querySelectorAll('.fade-in-on-scroll');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.15 });
    cards.forEach(card => observer.observe(card));

    // Mobile Navigation Toggle
    const navToggle = document.querySelector('.nav-toggle');
    const navMenu = document.querySelector('.nav-menu');
    
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function() {
            navMenu.classList.toggle('active');
        });
    }
    
    // Close mobile nav when clicking on links
    document.querySelectorAll('.nav-menu a').forEach(link => {
        link.addEventListener('click', function() {
            if (navMenu) {
                navMenu.classList.remove('active');
            }
        });
    });

    // Navigation scroll behavior (similar to basecamp)
    let lastScrollTop = 0;
    let scrollTimer = null;
    const navigation = document.querySelector('.main-navigation');
    
    if (navigation) {
        window.addEventListener('scroll', function() {
            const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
            
            // Clear any existing timer
            if (scrollTimer) {
                clearTimeout(scrollTimer);
            }
            
            // Show navbar while scrolling
            navigation.classList.remove('nav-hidden');
            
            // Hide navbar when scrolling down and past 100px
            if (scrollTop > lastScrollTop && scrollTop > 100) {
                scrollTimer = setTimeout(function() {
                    navigation.classList.add('nav-hidden');
                }, 300);
            } else {
                navigation.classList.remove('nav-hidden');
            }
            
            lastScrollTop = scrollTop;
        });
        
        // Show navbar on hover when hidden
        navigation.addEventListener('mouseenter', function() {
            this.classList.remove('nav-hidden');
        });
    }
}); 