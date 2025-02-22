const hamburger = document.querySelector(".hamburger");
const navMenu = document.querySelector(".nav-menu");

hamburger.addEventListener("click", () => {
  // Toggle active class on hamburger and nav menu
  hamburger.classList.toggle("active");
  navMenu.classList.toggle("active");
});

// Close menu when clicking a link (optional)
document.querySelectorAll(".nav-menu a").forEach((link) => {
  link.addEventListener("click", () => {
    hamburger.classList.remove("active");
    navMenu.classList.remove("active");
  });
});

let currentPage = 1;
const postsPerPage = 6;

async function loadPosts(page = 1) {
  const response = await fetch(
    `/api/posts?page=${page}&per_page=${postsPerPage}`
  );
  const data = await response.json();

  const container = document.getElementById("posts-container");
  container.innerHTML = data.posts
    .map(
      (post) => `
            <div class="post-card" onclick="openPost(${post.id})">
                ${
                  post.images && post.images.length > 0
                    ? `<img src="/static/uploads/${post.images[0]}" alt="Post image" class="post-thumbnail">`
                    : ""
                }
                <h2>${post.title}</h2>
                <p>${post.content.substring(0, 150)}...</p>
                <div class="post-meta">
                    <span class="author">By ${post.author}</span>
                    <span class="date">${new Date(
                      post.created_date
                    ).toLocaleString("en-US", {
                      timeZone: "America/Chicago",
                    })}</span>
                </div>
            </div>
        `
    )
    .join("");

  // Update pagination
  updatePagination(data.current_page, data.total_pages);
}

function updatePagination(currentPage, totalPages) {
  const prevBtn = document.getElementById("prev-page");
  const nextBtn = document.getElementById("next-page");
  const pageNumbers = document.getElementById("page-numbers");

  // Update previous/next buttons
  prevBtn.disabled = currentPage <= 1;
  nextBtn.disabled = currentPage >= totalPages;

  // Update page numbers
  pageNumbers.innerHTML = "";

  // Calculate range of pages to show
  let start = Math.max(1, currentPage - 2);
  let end = Math.min(totalPages, currentPage + 2);

  // Always show first page
  if (start > 1) {
    pageNumbers.innerHTML += `
            <span class="page-number" onclick="loadPosts(1)">1</span>
            ${start > 2 ? "<span>...</span>" : ""}
        `;
  }

  // Show page numbers
  for (let i = start; i <= end; i++) {
    pageNumbers.innerHTML += `
            <span class="page-number ${i === currentPage ? "active" : ""}" 
                  onclick="loadPosts(${i})">${i}</span>
        `;
  }

  // Always show last page
  if (end < totalPages) {
    pageNumbers.innerHTML += `
            ${end < totalPages - 1 ? "<span>...</span>" : ""}
            <span class="page-number" onclick="loadPosts(${totalPages})">${totalPages}</span>
        `;
  }
}

// Add event listeners for pagination buttons
document.getElementById("prev-page").addEventListener("click", () => {
  if (currentPage > 1) {
    currentPage--;
    loadPosts(currentPage);
  }
});

document.getElementById("next-page").addEventListener("click", () => {
  currentPage++;
  loadPosts(currentPage);
});
