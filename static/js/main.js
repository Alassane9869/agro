// Smooth reveal for hero image and smooth scrolling for anchor links
document.addEventListener('DOMContentLoaded', function(){
  const img = document.querySelector('.hero-image');
  if(img){
    requestAnimationFrame(()=>{
      img.style.opacity = '1';
      img.style.transform = 'translateY(0)';
    });
  }

  // Smooth scroll for internal links
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e){
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if(target){
        target.scrollIntoView({behavior:'smooth',block:'start'});
      }
    });
  });

  // Auth form UX
  const form = document.getElementById('auth-form');
  const submitBtn = document.getElementById('submit-btn');

  if(form && submitBtn){
    form.addEventListener('submit', () => {
      submitBtn.classList.add('is-loading');
      submitBtn.disabled = true;
    });

    // Optional: small focus feedback
    form.querySelectorAll('input').forEach(input => {
      input.addEventListener('focus', () => {
        input.closest('.field')?.classList.add('field-focused');
      });
      input.addEventListener('blur', () => {
        input.closest('.field')?.classList.remove('field-focused');
      });
    });
  }

  // =========================================================
  // Cultures dashboard (mock data, client-side filters + cards)
  // =========================================================
  const dataEl = document.getElementById('cultures-mock-data');
  if(dataEl){
    let data;
    try{ data = JSON.parse(dataEl.textContent); }catch(e){ data = null; }

    if(data && Array.isArray(data.cultures)){
      const cultures = data.cultures;

      // Stats (best-effort, based on mock)
      const setStat = (selector, value) => {
        const el = document.querySelector(selector);
        if(el) el.textContent = value;
      };

      const totalCultures = cultures.length;
      const growing = cultures.filter(c => (c.etat || c.etat_sante || '').toLowerCase().includes('croissant') || (c.etat || '').toLowerCase() === 'en croissance').length;
      const ready = cultures.filter(c => (c.etat || c.etat_sante || '').toLowerCase().includes('prêt') || (c.etat || '').toLowerCase().includes('pret') || (c.etat || '').toLowerCase().includes('recolte')).length;
      const parcelsCount = (data.parcelles && data.parcelles.length) ? data.parcelles.length : new Set(cultures.map(c=>c.parcelle)).size;
      const harvestsDone = (data.recoltes && data.recoltes.length) ? data.recoltes.length : 0;
      // Revenus et alertes calculés depuis les données mockées
      const revenues = harvestsDone * 125000; // estimation ~125k FCFA par récolte
      const importantAlerts = cultures.filter(c => (c.etat_sante || c.etat || '').toLowerCase().includes('risque')).length;

      setStat('[data-stat="total_cultures"]', totalCultures);
      setStat('[data-stat="growing_cultures"]', growing);
      setStat('[data-stat="ready_cultures"]', ready);
      setStat('[data-stat="total_parcels"]', parcelsCount);
      setStat('[data-stat="harvests_done"]', harvestsDone);
      setStat('[data-stat="revenues"]', revenues);
      setStat('[data-stat="important_alerts"]', importantAlerts);

      // Search & filters
      const searchInput = document.getElementById('culture-search');
      const fCategory = document.getElementById('filter-category');
      const fSeason = document.getElementById('filter-season');
      const fParcel = document.getElementById('filter-parcel');
      const fStatus = document.getElementById('filter-status');
      const fSeedDate = document.getElementById('filter-seed-date');
      const resetBtn = document.getElementById('btn-reset-filters');

      const container = document.getElementById('cultures-container');
      const followContainer = document.getElementById('follow-container');
      const timelineContainer = document.getElementById('timeline-container');
      const alertsContainer = document.getElementById('alerts-container');

      const escapeHtml = (s) => String(s ?? '').replace(/[&<>"']/g, m => ({'&':'&amp;','<':'<','>':'>','"':'"','\'':'&#39;'}[m]));

      const matches = (culture) => {
        const q = (searchInput?.value || '').trim().toLowerCase();
        if(q){
          const name = (culture.nom || '').toLowerCase();
          if(!name.includes(q)) return false;
        }

        const cat = fCategory?.value || '';
        if(cat && (culture.categorie || '') !== cat) return false;

        const saison = fSeason?.value || '';
        // Mock ne contient pas season => garder filtrage neutre si champ absent
        if(saison && culture.saison && culture.saison !== saison) return false;

        const parc = fParcel?.value || '';
        if(parc && (culture.parcelle || '') !== parc) return false;

        const status = fStatus?.value || '';
        if(status && (culture.etat || '') !== status) return false;

        const seed = fSeedDate?.value || '';
        if(seed){
          // comparer sur YYYY-MM-DD
          if(String(culture.date_semis || '').slice(0,10) !== seed) return false;
        }

        return true;
      };

      const progress = (culture) => {
        const pct = Number(culture.pourcentage_croissance ?? 0);
        const safe = Math.max(0, Math.min(100, pct));
        return safe;
      };

      const cultureCard = (culture) => {
        const pct = progress(culture);
        const seed = culture.date_semis || '';
        const harvest = culture.date_estimee_recolte || '';
        const photo = culture.photo || '';

        const etat = culture.etat || '';
          // état de santé : indicateur (réutilisable plus tard si tu ajoutes un badge)
          // const stateTone = etat.toLowerCase().includes('risque') || etat.toLowerCase().includes('à risque') ? 'warn' : (etat.toLowerCase().includes('prêt') ? 'ok' : 'neutral');

        const progressWidth = `${pct}%`;


        return `
          <article class="culture-card" data-culture-id="${escapeHtml(culture.id)}">
            <div class="culture-media">
              ${photo ? `<img src="${escapeHtml(photo)}" alt="${escapeHtml(culture.photo_alt || culture.nom || 'Culture')}" />` : ''}
            </div>
            <div class="culture-body">
              <div class="culture-title">
                <div>
                  <div class="culture-name">${escapeHtml(culture.nom)}</div>
                  <span class="pill"><i class="fa-solid fa-tag"></i>${escapeHtml(culture.categorie)}</span>
                </div>
                <div style="text-align:right">
                  <span class="pill" style="background: rgba(56,189,248,0.10); border-color: rgba(56,189,248,0.22); color:#0369a1">
                    <i class="fa-solid fa-location-dot"></i>${escapeHtml(culture.parcelle)}
                  </span>
                </div>
              </div>

              <div class="culture-meta">
                <div><span class="k">Superficie</span><div>${escapeHtml(culture.superficie)}</div></div>
                <div><span class="k">Semis</span><div>${escapeHtml(seed)}</div></div>
                <div><span class="k">Récolte estimée</span><div>${escapeHtml(harvest)}</div></div></div>
                <div><span class="k">Rendement</span><div>${escapeHtml(culture.rendement_attendu)}</div></div>
                <div><span class="k">État de santé</span><div>${escapeHtml(culture.etat_sante || culture.etat)}</div></div>
                <div><span class="k">Stade</span><div>${escapeHtml(culture.stade || '')}</div></div>
              </div>

              <div class="culture-progress">
                <div class="progress-label">
                  <span><i class="fa-solid fa-chart-line"></i> Croissance</span>
                  <strong>${pct}%</strong>
                </div>
                <div class="progress-bar" aria-label="Progression de croissance">
                  <span style="width:${progressWidth}"></span>
                </div>
              </div>

              <div class="culture-actions">
                <button type="button" class="btn btn-secondary" data-action="view" title="Voir">
                  <i class="fa-solid fa-eye me-2"></i>Voir
                </button>
                <button type="button" class="btn" data-action="edit" title="Modifier">
                  <i class="fa-solid fa-pen-to-square me-2"></i>Modifier
                </button>
                <button type="button" class="btn btn-secondary" data-action="delete" title="Supprimer" style="border-color: rgba(239,68,68,0.35); color: #ef4444">
                  <i class="fa-solid fa-trash me-2"></i>Supprimer
                </button>
              </div>
            </div>
          </article>
        `;
      };

      const renderCultures = () => {
        if(!container) return;
        const filtered = cultures.filter(matches);
        container.innerHTML = filtered.map(cultureCard).join('');

        // Bind simple click handlers (demo)
        container.querySelectorAll('button[data-action]').forEach(btn => {
          btn.addEventListener('click', () => {
            const card = btn.closest('[data-culture-id]');
            const id = card?.getAttribute('data-culture-id');
            const action = btn.getAttribute('data-action');

            // Modal actions (demo)
            const overlay = document.getElementById('modal-overlay');
            const modalBody = document.getElementById('modal-body');
            const modalFooter = document.getElementById('modal-footer');
            const modalClose = document.getElementById('modal-close');

            if(overlay && modalBody && modalFooter){
              const culture = cultures.find(c => String(c.id) === String(id));
              const cultureName = culture?.nom || 'Culture';

              const viewHtml = `
                <div class="modal-grid">
                  <div class="modal-field"><div class="lbl">Nom</div><div class="val">${escapeHtml(cultureName)}</div></div>
                  <div class="modal-field"><div class="lbl">Catégorie</div><div class="val">${escapeHtml(culture?.categorie || '')}</div></div>
                  <div class="modal-field"><div class="lbl">Parcelle</div><div class="val">${escapeHtml(culture?.parcelle || '')}</div></div>
                  <div class="modal-field"><div class="lbl">Superficie</div><div class="val">${escapeHtml(culture?.superficie || '')}</div></div>
                  <div class="modal-field"><div class="lbl">Semis</div><div class="val">${escapeHtml(culture?.date_semis || '')}</div></div>
                  <div class="modal-field"><div class="lbl">Récolte estimée</div><div class="val">${escapeHtml(culture?.date_estimee_recolte || '')}</div></div>
                  <div class="modal-field"><div class="lbl">Rendement attendu</div><div class="val">${escapeHtml(culture?.rendement_attendu || '')}</div></div>
                  <div class="modal-field"><div class="lbl">État de santé</div><div class="val">${escapeHtml(culture?.etat_sante || culture?.etat || '')}</div></div>
                </div>
              `;

              const editHtml = `
                <div class="small-muted" style="margin-bottom:.75rem"><i class="fa-solid fa-pen-to-square"></i> Édition (démo UI)</div>
                <div class="modal-grid">
                  <label class="modal-field"><div class="lbl">Nom</div><input id="modal-edit-nom" class="input" style="width:100%;border:none;outline:none;background:transparent;font-weight:950;color:#0f172a" value="${escapeHtml(culture?.nom || '')}" /></label>
                  <label class="modal-field"><div class="lbl">Parcelle</div><input id="modal-edit-parcelle" class="input" style="width:100%;border:none;outline:none;background:transparent;font-weight:950;color:#0f172a" value="${escapeHtml(culture?.parcelle || '')}" /></label>
                </div>
                <div class="small-muted" style="margin-top:.75rem">Aucune sauvegarde backend pour l’instant (mock).</div>
              `;

              const deleteHtml = `
                <div class="danger-text" style="color:#ef4444;font-weight:950;display:flex;align-items:center;gap:.6rem;margin-bottom:.75rem">
                  <i class="fa-solid fa-triangle-exclamation"></i> Confirmation de suppression
                </div>
                <div class="small-muted">Supprimer <strong>${escapeHtml(cultureName)}</strong> ? Cette action est une démo UI (aucune suppression réelle).</div>
              `;

              modalBody.innerHTML = action === 'view' ? viewHtml : (action === 'edit' ? editHtml : deleteHtml);

              const primaryBtn = action === 'delete'
                ? `<button class="btn" type="button" id="modal-confirm-delete"><i class="fa-solid fa-trash me-2"></i>Confirmer</button>`
                : `<button class="btn btn-primary" type="button" id="modal-confirm"><i class="fa-solid fa-check me-2"></i>OK</button>`;

              modalFooter.innerHTML = primaryBtn + `
                <button class="btn btn-secondary" type="button" id="modal-cancel"><i class="fa-solid fa-xmark me-2"></i>Annuler</button>
              `;

              overlay.classList.add('is-open');
              overlay.setAttribute('aria-hidden','false');

              const closeModal = () => {
                overlay.classList.remove('is-open');
                overlay.setAttribute('aria-hidden','true');
              };

              if(modalClose){
                modalClose.onclick = closeModal;
              }

              const cancel = document.getElementById('modal-cancel');
              if(cancel) cancel.onclick = closeModal;

              const confirm = document.getElementById('modal-confirm');
              if(confirm) confirm.onclick = closeModal;

              const confirmDelete = document.getElementById('modal-confirm-delete');
              if(confirmDelete) confirmDelete.onclick = () => {
                closeModal();
                console.log('Supprimer (UI demo) id:', id);
              };

              // click outside
              overlay.onclick = (e) => {
                if(e.target === overlay) closeModal();
              };
            } else {
              console.log('Culture action:', action, 'id:', id);
            }
          });
        });
      };

      const renderFollow = () => {
        if(!followContainer) return;
        const filtered = cultures.filter(matches).slice(0, 3);
        followContainer.innerHTML = filtered.map(c => `
          <article class="follow-card">
            <div class="follow-top">
              <div class="follow-title"><i class="fa-solid fa-seedling"></i> ${escapeHtml(c.nom)}</div>
              <span class="pill"><i class="fa-solid fa-layer-group"></i>${escapeHtml(c.parcelle)}</span>
            </div>
            <div class="small-muted">Stade de développement : <strong>${escapeHtml(c.stade || '')}</strong></div>
            <div class="small-muted">Pourcentage de croissance : <strong>${escapeHtml(c.pourcentage_croissance ?? c.pourcentage_croissance || c.pourcentage_croissance)}</strong></div>
            <div class="small-muted">Dernière intervention : <strong>${escapeHtml(c.derniere_intervention || '')}</strong></div>
            <div class="small-muted">Prochaine intervention : <strong>${escapeHtml(c.prochaine_intervention || '')}</strong></div>
          </article>
        `).join('');
      };

      const renderTimeline = () => {
        if(!timelineContainer) return;
        const items = (data.calendrier || []).slice(0, 8);
        const out = items.map(it => `
          <div class="timeline-item">
            <div class="timeline-meta">
              <span class="timeline-dot" aria-hidden="true"></span>
              <span class="timeline-date"><i class="fa-solid fa-calendar"></i> ${escapeHtml(it.date)}</span>
              <span class="timeline-action"><i class="fa-solid fa-list-check"></i> ${escapeHtml(it.action)}</span>
            </div>
            <div class="small-muted"><i class="fa-solid fa-seedling"></i> ${escapeHtml(it.culture)}</div>
          </div>
        `).join('');
        timelineContainer.innerHTML = out;
      };

      const renderAlerts = () => {
        if(!alertsContainer) return;
        const now = new Date('2026-06-27T00:00:00Z');
        const alerts = [];

        cultures.forEach(c => {
          const harvest = c.date_estimee_recolte ? new Date(c.date_estimee_recolte + 'T00:00:00Z') : null;
          const next = c.prochaine_intervention ? new Date(c.prochaine_intervention + 'T00:00:00Z') : null;
          const seed = c.date_semis ? new Date(c.date_semis + 'T00:00:00Z') : null;

          if(harvest){
            const diffDays = Math.round((harvest - now) / (1000*60*60*24));
            if(diffDays >= 0 && diffDays <= 25){
              alerts.push({
                type: 'warn',
                title: 'Récolte proche',
                text: `${c.nom} — récolte estimée le ${c.date_estimee_recolte} (≈ ${diffDays} jours).`,
              });
            }
          }

          if(next){
            const diffDays = Math.round((next - now) / (1000*60*60*24));
            if(diffDays >= 0 && diffDays <= 10){
              alerts.push({
                type: 'ok',
                title: 'Prochaine intervention',
                text: `${c.nom} — ${c.prochaine_intervention} : ${c.prochaine_intervention ? 'à planifier' : ''}`,
              });
            }
          }

          const health = (c.etat_sante || c.etat || '').toLowerCase();
          if(health.includes('risque')){
            alerts.push({
              type: 'danger',
              title: 'Traitement recommandé',
              text: `${c.nom} montre un état à risque. Vérifier les symptômes et renforcer le suivi.`,
            });
          }
        });

        // Stock faible (mock)
        alerts.push({type:'warn', title:'Stock faible', text:'Les réserves de semences sont en baisse. Programmer un réassort.'});

        // Render unique top 6
        const uniq = alerts.slice(0, 6);
        alertsContainer.innerHTML = uniq.map(a => {
          const cls = a.type === 'danger' ? 'danger' : (a.type === 'warn' ? 'warn' : 'ok');
          const badgeIcon = a.type === 'danger' ? 'fa-triangle-exclamation' : (a.type === 'warn' ? 'fa-bell' : 'fa-check-circle');
          return `
            <div class="alert-card ${cls}">
              <div class="alert-badge"><i class="fa-solid ${badgeIcon}"></i></div>
              <div>
                <div class="alert-title">${escapeHtml(a.title)}</div>
                <div class="alert-text">${escapeHtml(a.text)}</div>
              </div>
            </div>
          `;
        }).join('');
      };

      // Sanitary section (render once; not filtered)
      const sanitaryContainer = document.getElementById('sanitary-container');
      if(sanitaryContainer){
        const sani = data.sanitaire || [];
        if(Array.isArray(sani) && sani.length){
          sanitaryContainer.innerHTML = sani.map(s => `
            <article class="sanitary-card">
              <h4><i class="fa-solid fa-stethoscope"></i> ${escapeHtml(s.culture)}</h4>
              <div class="small-muted"><strong>Maladie</strong> : ${escapeHtml(s.maladie)}</div>
              <div class="small-muted"><strong>Ravageurs</strong> : ${escapeHtml(s.ravageurs)}</div>
              <div class="small-muted"><strong>Symptômes</strong> : ${escapeHtml(s.symptomes)}</div>
              <div>
                <div class="small-muted" style="margin-bottom:.35rem"><strong>Traitements appliqués</strong></div>
                <ul class="list-compact">${(s.traitements||[]).map(t=>`<li>${escapeHtml(t.nom)} — ${escapeHtml(t.date)}</li>`).join('')}</ul>
              </div>
              <div class="small-muted"><strong>Résultats</strong> : ${escapeHtml(s.resultats)}</div>
            </article>
          `).join('');
        }
      }

      const expensesContainer = document.getElementById('expenses-container');
      const expensesTotal = document.getElementById('expenses-total');
      if(expensesContainer){
        const deps = data.depenses || [];
        const total = deps.reduce((sum, d) => sum + Number(d.montant || 0), 0);
        expensesContainer.innerHTML = deps.map(d => `
          <div class="expense-card">
            <div class="expense-title"><i class="fa-solid fa-wallet"></i> ${escapeHtml(d.categorie)}</div>
            <div class="expense-amount">${new Intl.NumberFormat('fr-FR').format(Number(d.montant||0))} ${escapeHtml(d.devise||'')}</div>
          </div>
        `).join('');
        if(expensesTotal) expensesTotal.textContent = `${new Intl.NumberFormat('fr-FR').format(total)} FCFA`;
      }

      const harvestContainer = document.getElementById('harvest-container');
      if(harvestContainer){
        const recs = data.recoltes || [];
        harvestContainer.innerHTML = recs.map(r => {
          const dest = r.destination || 'Stock';
          const tagCls = dest.toLowerCase().includes('vente') ? '' : 'stock';
          return `
            <article class="harvest-card">
              <div style="display:flex;justify-content:space-between;gap:1rem;align-items:flex-start">
                <div>
                  <div class="follow-title"><i class="fa-solid fa-basket-shopping"></i> ${escapeHtml(r.culture)}</div>
                  <div class="small-muted">Date : <strong>${escapeHtml(r.date)}</strong></div>
                </div>
                <span class="tag ${tagCls}"><i class="fa-solid fa-warehouse"></i> ${escapeHtml(dest)}</span>
              </div>
              <div class="small-muted">Quantité : <strong>${escapeHtml(r.quantite)}</strong></div>
              <div class="small-muted">Qualité : <strong>${escapeHtml(r.qualite)}</strong></div>
            </article>
          `;
        }).join('');
      }

      // Charts mock initialization (if chart.js exists)
      const ChartLib = window.Chart;
      const charts = data.charts || {};
      if(ChartLib){
        const mk = (canvasId, cfg) => {
          const el = document.getElementById(canvasId);
          if(!el) return;
          new ChartLib(el, cfg);
        };

        mk('chart-production', {
          type: 'bar',
          data: { labels: charts.production?.labels || [], datasets: [{ label: 'Production', data: charts.production?.values || [], backgroundColor: 'rgba(20,184,166,0.55)', borderColor: 'rgba(20,184,166,0.95)', borderWidth: 1 }] },
          options: { responsive: true, plugins:{ legend:{ display:false }}, scales:{ y:{ beginAtZero:true } } }
        });

        mk('chart-distribution', {
          type: 'doughnut',
          data: { labels: charts.distribution?.labels || [], datasets: [{ data: charts.distribution?.values || [], backgroundColor: ['rgba(56,189,248,0.65)','rgba(20,184,166,0.55)','rgba(14,165,233,0.50)'] }] },
          options: { responsive: true, plugins:{ legend:{ position:'bottom' } } }
        });

        mk('chart-yield', {
          type: 'line',
          data: { labels: charts.yield?.labels || [], datasets: [{ label: 'Rendement', data: charts.yield?.values || [], borderColor: 'rgba(56,189,248,0.95)', backgroundColor: 'rgba(56,189,248,0.12)', tension: 0.35, fill:true }] },
          options: { responsive: true, plugins:{ legend:{ display:false }}, scales:{ y:{ beginAtZero:false } } }
        });

        mk('chart-harvest-evolution', {
          type: 'bar',
          data: { labels: charts.harvest_evolution?.labels || [], datasets: [{ data: charts.harvest_evolution?.values || [], backgroundColor: 'rgba(56,189,248,0.35)', borderColor: 'rgba(56,189,248,0.95)', borderWidth: 1 }] },
          options: { responsive: true, plugins:{ legend:{ display:false }}, scales:{ y:{ beginAtZero:true } } }
        });
      }

      // Bind events
      const rerenderAll = () => {
        // Re-render filtered parts
        renderCultures();
        renderFollow();

        // If alerts should react to filters, uncomment:
        // renderAlerts();
      };

      [searchInput,fCategory,fSeason,fParcel,fStatus,fSeedDate].forEach(el => {
        if(el) el.addEventListener('input', rerenderAll);
        if(el) el.addEventListener('change', rerenderAll);
      });

      if(resetBtn){
        resetBtn.addEventListener('click', () => {
          if(searchInput) searchInput.value = '';
          if(fCategory) fCategory.value = '';
          if(fSeason) fSeason.value = '';
          if(fParcel) fParcel.value = '';
          if(fStatus) fStatus.value = '';
          if(fSeedDate) fSeedDate.value = '';
          renderCultures();
          renderFollow();
        });
      }

      // initial render
      renderCultures();
      renderFollow();
      renderTimeline();
      renderAlerts();
    }
  }
});


