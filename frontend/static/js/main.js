/**
 * main.js — Landing page interactions (nav scroll, etc.)
 */

document.addEventListener('DOMContentLoaded', () => {
  // Sticky nav shadow on scroll
  const nav = document.querySelector('.nav');
  window.addEventListener('scroll', () => {
    nav?.classList.toggle('nav--scrolled', window.scrollY > 10);
  });
});
