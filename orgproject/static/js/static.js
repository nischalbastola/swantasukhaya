  // Fade-in effect for sections
  document.addEventListener("DOMContentLoaded", function() {
    document.querySelectorAll('.fade-in').forEach(function(el, i) {
        setTimeout(() => {
            el.style.opacity = 1;
            el.style.transform = "none";
        }, 200 + i * 200);
    });
});