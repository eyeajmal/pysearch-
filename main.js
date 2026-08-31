function renderCard(item) {
  // Safe fallback if the page has no thumbnail
  const imageHtml = item.thumbnail 
    ? `<img src="${item.thumbnail}" alt="${item.title}" class="result-thumb" />` 
    : `<div class="thumb-placeholder">📄</div>`;

  return `
    <div class="result-card">
      <div class="card-content">
        <a href="${item.url}" target="_blank" class="result-url">${item.url}</a>
        <h3 class="result-title">${item.title}</h3>
        <p class="result-snippet">${item.snippet}</p>
      </div>
      <div class="card-media">
        ${imageHtml}
      </div>
    </div>
  `;
}