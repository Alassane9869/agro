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
  if (chartCanvas) {
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
          label: 'Activités',
          data: chartData,
          backgroundColor: ['#2E7D32', '#4CAF50', '#A5D6A7', '#F9A825', '#14B8A6', '#F59E0B'],
          borderRadius: 12
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true } }
      }
    });
  }
});
