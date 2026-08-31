document.addEventListener('DOMContentLoaded', () => {
  // === 1. GESTION DU THÈME JOUR / NUIT (LIGHT / DARK MODE) ===
  const themeToggleBtns = document.querySelectorAll('.btn-theme-toggle');
  const themeMetaColor = document.getElementById('theme-meta-color');
  
  const getPreferredTheme = () => {
    const saved = localStorage.getItem('agrosedam_theme');
    if (saved) return saved;
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark';
  };

  const updateThemeUI = (theme) => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('agrosedam_theme', theme);
    
    if (themeMetaColor) {
      themeMetaColor.setAttribute('content', theme === 'light' ? '#f8fafc' : '#090e17');
    }

    themeToggleBtns.forEach(btn => {
      const icon = btn.querySelector('.theme-icon');
      if (icon) {
        if (theme === 'light') {
          icon.classList.remove('fa-sun');
          icon.classList.add('fa-moon');
          btn.setAttribute('title', 'Passer en mode Nuit');
        } else {
          icon.classList.remove('fa-moon');
          icon.classList.add('fa-sun');
          btn.setAttribute('title', 'Passer en mode Jour');
        }
      }
    });

    if (window.agrosedamActivityChart) {
      const isLight = theme === 'light';
      const textColor = isLight ? '#475569' : '#94a3b8';
      const gridColor = isLight ? 'rgba(0, 0, 0, 0.06)' : 'rgba(255, 255, 255, 0.05)';
      
      window.agrosedamActivityChart.options.scales.x.ticks.color = textColor;
      window.agrosedamActivityChart.options.scales.x.grid.color = gridColor;
      window.agrosedamActivityChart.options.scales.y.ticks.color = textColor;
      window.agrosedamActivityChart.options.scales.y.grid.color = gridColor;
      window.agrosedamActivityChart.update();
    }
  };

  const currentTheme = getPreferredTheme();
  updateThemeUI(currentTheme);

  themeToggleBtns.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      const activeTheme = document.documentElement.getAttribute('data-theme') || 'dark';
      const newTheme = activeTheme === 'dark' ? 'light' : 'dark';
      updateThemeUI(newTheme);
    });
  });

  // === 2. GESTION PWA AUTOMATIQUE & INSTALLATION RAPIDE ===
  let deferredPrompt = null;
  const pwaBanner = document.getElementById('pwa-banner');
  const desktopPwaBtn = document.getElementById('desktop-pwa-btn');
  const mobilePwaBtn = document.getElementById('mobile-pwa-btn');
  const pwaInstallTrigger = document.getElementById('pwa-install-trigger');
  const pwaCloseBanner = document.getElementById('pwa-close-banner');

  const isStandalone = window.matchMedia('(display-mode: standalone)').matches || window.navigator.standalone === true;
  const isIos = /iphone|ipad|ipod/i.test(window.navigator.userAgent.toLowerCase());

  // Enregistrement du Service Worker
  if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
      navigator.serviceWorker.register('/service-worker.js')
        .then((reg) => console.log('PWA Service Worker actif:', reg.scope))
        .catch((err) => console.log('Service Worker non supporté:', err));
    });
  }

  const showInstallPrompts = () => {
    if (isStandalone) return; // Déjà installée

    const bannerDismissed = localStorage.getItem('agrosedam_pwa_dismissed');
    if (pwaBanner && !bannerDismissed) {
      setTimeout(() => {
        pwaBanner.style.display = 'block';
      }, 1500);
    }
    if (desktopPwaBtn) desktopPwaBtn.classList.remove('d-none');
    if (mobilePwaBtn) mobilePwaBtn.classList.remove('d-none');
  };

  // Événement avant installation natif (Chrome, Android, Edge, PC/Mac)
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    showInstallPrompts();
  });

  // Pour iOS / Safari, afficher le bouton PWA qui ouvre le guide modal
  if (isIos && !isStandalone) {
    showInstallPrompts();
  }

  const triggerPwaInstall = () => {
    if (deferredPrompt) {
      deferredPrompt.prompt();
      deferredPrompt.userChoice.then((choiceResult) => {
        if (choiceResult.outcome === 'accepted') {
          console.log('AgroSedam installé !');
          if (pwaBanner) pwaBanner.style.display = 'none';
          if (desktopPwaBtn) desktopPwaBtn.classList.add('d-none');
          if (mobilePwaBtn) mobilePwaBtn.classList.add('d-none');
        }
        deferredPrompt = null;
      });
    } else if (isIos) {
      // Ouvrir le modal spécifique Apple
      const iosModalEl = document.getElementById('iosPwaModal');
      if (iosModalEl && typeof bootstrap !== 'undefined') {
        const modal = new bootstrap.Modal(iosModalEl);
        modal.show();
      }
    }
  };

  if (pwaInstallTrigger) pwaInstallTrigger.addEventListener('click', triggerPwaInstall);
  if (desktopPwaBtn) desktopPwaBtn.addEventListener('click', triggerPwaInstall);
  if (mobilePwaBtn) mobilePwaBtn.addEventListener('click', triggerPwaInstall);

  if (pwaCloseBanner) {
    pwaCloseBanner.addEventListener('click', () => {
      if (pwaBanner) pwaBanner.style.display = 'none';
      localStorage.setItem('agrosedam_pwa_dismissed', 'true');
    });
  }

  // === 3. NAVBAR & ANIMATIONS SCROLL ===
  const navbar = document.querySelector('.navbar-glass');
  const revealItems = document.querySelectorAll('.reveal');
  const counters = document.querySelectorAll('.counter-value');

  const handleScroll = () => {
    if (window.scrollY > 12) {
      navbar?.classList.add('scrolled');
    } else {
      navbar?.classList.remove('scrolled');
    }

    revealItems.forEach((item) => {
      const top = item.getBoundingClientRect().top;
      if (top < window.innerHeight - 80) {
        item.classList.add('is-visible');
      }
    });
  };

  counters.forEach((counter) => {
    const target = Number(counter.dataset.target || 0);
    let current = 0;
    const duration = 1200;
    const start = performance.now();
    const step = (timestamp) => {
      const progress = Math.min((timestamp - start) / duration, 1);
      current = Math.floor(progress * target);
      counter.textContent = current.toLocaleString('fr-FR');
      if (progress < 1) requestAnimationFrame(step);
      else counter.textContent = target.toLocaleString('fr-FR');
    };
    requestAnimationFrame(step);
  });

  handleScroll();
  window.addEventListener('scroll', handleScroll, { passive: true });

  // === 4. GRAPHIQUE DASHBOARD CHART.JS ===
  const chartCanvas = document.getElementById('activity-chart') || document.getElementById('operationsChart');
  if (chartCanvas && typeof Chart !== 'undefined') {
    const ctx = chartCanvas.getContext('2d');
    const readData = (attr) => Number(chartCanvas.dataset[attr] || 0);
    const chartData = [
      readData('crops'),
      readData('animals'),
      readData('plots'),
      readData('poultries'),
      readData('incubators'),
      readData('harvests'),
    ];
    
    const isLight = document.documentElement.getAttribute('data-theme') === 'light';
    const textColor = isLight ? '#475569' : '#94a3b8';
    const gridColor = isLight ? 'rgba(0, 0, 0, 0.06)' : 'rgba(255, 255, 255, 0.05)';

    window.agrosedamActivityChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: ['Cultures', 'Animaux', 'Parcelles', 'Volailles', 'Incubations', 'Récoltes'],
        datasets: [{
          label: 'Activités enregistrées',
          data: chartData,
          backgroundColor: [
            'rgba(16, 185, 129, 0.85)',
            'rgba(13, 148, 136, 0.85)',
            'rgba(59, 130, 246, 0.85)',
            'rgba(245, 158, 11, 0.85)',
            'rgba(139, 92, 246, 0.85)',
            'rgba(236, 72, 153, 0.85)'
          ],
          borderColor: [
            '#10b981',
            '#0d9488',
            '#3b82f6',
            '#f59e0b',
            '#8b5cf6',
            '#ec4899'
          ],
          borderWidth: 1,
          borderRadius: 8
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { 
          legend: { display: false },
          tooltip: {
            backgroundColor: 'rgba(15, 23, 42, 0.95)',
            titleColor: '#fff',
            bodyColor: '#cbd5e1',
            borderColor: 'rgba(16, 185, 129, 0.3)',
            borderWidth: 1,
            padding: 12,
            cornerRadius: 10
          }
        },
        scales: { 
          x: {
            grid: { color: gridColor },
            ticks: { color: textColor, font: { family: 'Plus Jakarta Sans', weight: '600' } }
          },
          y: { 
            beginAtZero: true,
            grid: { color: gridColor },
            ticks: { color: textColor, font: { family: 'Plus Jakarta Sans' }, precision: 0 }
          } 
        }
      }
    });
  }
});
