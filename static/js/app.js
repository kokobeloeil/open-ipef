(function () {
  "use strict";

  // Menu mobile
  const toggle = document.querySelector("[data-nav-toggle]");
  const nav = document.querySelector("[data-nav]");
  if (toggle && nav) {
    toggle.addEventListener("click", () => {
      const open = nav.classList.toggle("open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
  }

  // Fermer le menu utilisateur en cliquant ailleurs
  document.addEventListener("click", (e) => {
    document.querySelectorAll("details.user-menu[open]").forEach((d) => {
      if (!d.contains(e.target)) d.removeAttribute("open");
    });
  });

  // Confirmation avant une action destructive
  document.querySelectorAll("form[data-confirm]").forEach((form) => {
    form.addEventListener("submit", (e) => {
      if (!window.confirm(form.dataset.confirm)) e.preventDefault();
    });
  });

  // Envoi automatique à la sélection
  document.querySelectorAll("[data-autosubmit]").forEach((el) => {
    el.addEventListener("change", () => el.form && el.form.submit());
  });

  // Messages refermables
  document.querySelectorAll(".message button").forEach((btn) => {
    btn.addEventListener("click", () => btn.closest(".message").remove());
  });

  // Afficher le motif de refus uniquement si nécessaire
  document.querySelectorAll("[data-refus-toggle]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const form = btn.closest(".mod-actions").querySelector(".refus-form");
      form.hidden = !form.hidden;
      if (!form.hidden) form.querySelector("input[type=text]").focus();
    });
  });

  // Apparition douce au défilement
  const items = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window && items.length) {
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.08 }
    );
    items.forEach((el, i) => {
      el.style.transitionDelay = `${Math.min(i % 6, 5) * 60}ms`;
      io.observe(el);
    });
  } else {
    items.forEach((el) => el.classList.add("visible"));
  }
})();
