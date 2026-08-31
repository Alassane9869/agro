document.addEventListener('DOMContentLoaded', () => {
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
    
    new Chart(ctx, {
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
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans', weight: '600' } }
          },
          y: { 
            beginAtZero: true,
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94a3b8', font: { family: 'Plus Jakarta Sans' }, precision: 0 }
          } 
        }
      }
    });
  }
});
