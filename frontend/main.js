const API_URL = 'http://localhost:5000/api/posts';
const postsContainer = document.getElementById('posts');

function formatFecha(fechaStr) {
  if (!fechaStr) return "";
  const date = new Date(fechaStr);
  return date.toLocaleString('es-ES', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' });
}

async function fetchPosts() {
  try {
    const response = await fetch(API_URL);
    const posts = await response.json();
    renderPosts(posts);
  } catch (err) {
    postsContainer.innerHTML = `<p class="error">Error cargando noticias</p>`;
  }
}

function renderPosts(posts) {
  if (!posts.length) {
    postsContainer.innerHTML = "<p>No hay noticias aún.</p>";
    return;
  }
  postsContainer.innerHTML = posts.map(post => `
    <div class="card">
      ${post.image_url ? `<img src="${post.image_url}" alt="Imagen noticia">` : ""}
      <div class="card-title">${post.title}</div>
      <div class="card-summary">${post.summary}</div>
      <div class="card-date">${formatFecha(post.created_at)}</div>
    </div>
  `).join('');
}

// Recarga cada 30 segundos
fetchPosts();
setInterval(fetchPosts, 30000);
