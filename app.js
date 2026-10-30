'use strict';

const modules = [
  { id: 'conversation', tag: 'THE DIALOGUE', title: 'Space to start a conversation.', description: 'A focused dialogue area, with your care workspace alongside it. Talk at your pace and revisit the recent exchange.', alt: 'Conversation module with an illustrative exchange between a user and Digital Doctor.' },
  { id: 'care-map', tag: 'THE CURRENT RESPONSE', title: 'Follow the focus, as it changes.', description: 'The care guide highlights the current skill and selected response move. See where the platform is focusing as the dialogue unfolds.', alt: 'Live Care Map with the doctor guide, active OCD / ERP skill, Reflect response move, and current phase.' },
  { id: 'skills', tag: 'THE SKILL LIBRARY', title: 'Look inside the skill being used.', description: 'Search registered skills by name or topic. Expand the active skill to explore its available response moves.', alt: 'Skill Bank showing the registered OCD / ERP skill and an expandable list of response moves.' },
  { id: 'milestones', tag: 'THE CARE PATH', title: 'Progress with a visible direction.', description: 'See completed, active, and upcoming phases in the Milestone Map. The path follows readiness, rather than a fixed number of turns.', alt: 'Milestone Map showing Assessment and Formulation completed, ERP Buy-In active, and subsequent phases pending.' },
  { id: 'memory', tag: 'THE CONTINUITY', title: 'Keep the context in view.', description: 'Browse recent dialogue alongside longer-term summaries, topics, and reminders. Each profile carries its own conversation context.', alt: 'Memory Cabinet showing a clearly illustrative continuity summary, remembered topics, and a reminder.' },
  { id: 'formulation', tag: 'THE EMERGING PICTURE', title: 'Bring the patterns together.', description: 'Structured case notes collect the concerns, triggers, and recurring patterns emerging in the conversation.', alt: 'Case Formulation displaying illustrative structured notes about a concern, a trigger, and a checking ritual.' }
];

const tabs = [...document.querySelectorAll('.module-tab')];
const panel = document.getElementById('module-panel');
const image = document.getElementById('module-image');
let activeIndex = 0;

function selectModule(index, focus = false) {
  activeIndex = (index + modules.length) % modules.length;
  const item = modules[activeIndex];
  tabs.forEach((tab, i) => {
    tab.setAttribute('aria-selected', String(i === activeIndex));
    tab.tabIndex = i === activeIndex ? 0 : -1;
  });
  panel.setAttribute('aria-labelledby', tabs[activeIndex].id);
  panel.dataset.view = item.id;
  document.getElementById('module-tag').textContent = item.tag;
  document.getElementById('module-counter').textContent = `${String(activeIndex + 1).padStart(2, '0')} / 06`;
  document.getElementById('module-title').textContent = item.title;
  document.getElementById('module-description').textContent = item.description;
  image.src = `assets/module-${item.id}.png`;
  image.alt = item.alt;
  if (focus) tabs[activeIndex].focus();
}

tabs.forEach((tab, index) => {
  tab.addEventListener('click', () => selectModule(index));
  tab.addEventListener('keydown', event => {
    let next;
    if (event.key === 'ArrowDown' || event.key === 'ArrowRight') next = index + 1;
    if (event.key === 'ArrowUp' || event.key === 'ArrowLeft') next = index - 1;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = modules.length - 1;
    if (next !== undefined) {
      event.preventDefault();
      selectModule(next, true);
    }
  });
});
document.getElementById('next-module').addEventListener('click', () => selectModule(activeIndex + 1));

const video = document.getElementById('product-video');
const cover = document.getElementById('film-play');
async function playFilm() {
  cover.hidden = true;
  try {
    await video.play();
  } catch (_) {
    cover.hidden = false;
  }
}
cover.addEventListener('click', playFilm);
document.querySelectorAll('[data-watch]').forEach(link => link.addEventListener('click', playFilm));
video.addEventListener('play', () => { cover.hidden = true; });
video.addEventListener('ended', () => { cover.hidden = false; });

// Load the next module's lightweight image after the initial page is ready.
window.addEventListener('load', () => {
  for (const item of modules.slice(1)) {
    const preview = new Image();
    preview.src = `assets/module-${item.id}.png`;
  }
});
