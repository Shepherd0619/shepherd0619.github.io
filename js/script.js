// Portfolio Item Filter
const filterContainer = document.querySelector(".portfolio-filter"),
    filterBtns = filterContainer.children,
    totalFilterBtn = filterBtns.length,
    portfolioItems = document.querySelectorAll(".portfolio-item"),
    totalPortfolioItem = portfolioItems.length;

for (let i = 0; i < totalFilterBtn; i++) {
    filterBtns[i].addEventListener("click", function () {
        filterContainer.querySelector(".active").classList.remove("active")
        this.classList.add("active");

        const filterValue = this.getAttribute("data-filter");
        for (let k = 0; k < totalPortfolioItem; k++) {
            if (filterValue === portfolioItems[k].getAttribute("data-category")) {
                portfolioItems[k].classList.remove("hide");
                portfolioItems[k].classList.add("show");
            }
            else {
                portfolioItems[k].classList.remove("show")
                portfolioItems[k].classList.add("hide")
            }
            if (filterValue === "all") {
                portfolioItems[k].classList.remove("hide");
                portfolioItems[k].classList.add("show");
            }
        }

    })
}



// Portfolio Lightbox

const lightbox = document.querySelector(".lightbox"),
    lightboxImg = lightbox.querySelector(".lightbox-img"),
    lightboxClose = lightbox.querySelector(".lightbox-close"),
    lightboxText = lightbox.querySelector(".caption-text"),
    lightboxCounter = lightbox.querySelector(".caption-counter");
let itemIndex = 0;

for (let i = 0; i < totalPortfolioItem; i++) {
    portfolioItems[i].addEventListener("click", function () {
        itemIndex = i;
        changeItem();
        toggleLightbox();
    })
}

function nextItem() {
    if (itemIndex === totalPortfolioItem - 1) {
        itemIndex = 0
    }
    else {
        itemIndex++
    }
    changeItem()
}
function prevItem() {
    if (itemIndex === 0) {
        itemIndex = totalPortfolioItem - 1
    }
    else {
        itemIndex--;
    }
    changeItem()
}
//Body.......
function toggleLightbox() {
    lightbox.classList.toggle("open");
}

function changeItem() {
    imgSrc = portfolioItems[itemIndex].querySelector(".portfolio-img img").getAttribute("src");
    lightboxImg.src = imgSrc;
    lightboxText.innerHTML = portfolioItems[itemIndex].querySelector("h4").innerHTML;
    lightboxCounter.innerHTML = (itemIndex + 1) + " of " + totalPortfolioItem;
}

// Close Lightbox
lightbox.addEventListener("click", function (event) {
    if (event.target === lightboxClose || event.target === lightbox) {
        toggleLightbox();
    }

})


// Aside Navbar

const nav = document.querySelector(".nav"),
    navList = nav.querySelectorAll("li"),
    totalNavList = navList.length,
    allSection = document.querySelectorAll(".section"),
    totalSection = allSection.length;

for (let i = 0; i < totalNavList; i++) {
    const a = navList[i].querySelector("a");
    a.addEventListener("click", function () {
        // remove back secion
        removeBackSectionClass();

        for (let i = 0; i < totalSection; i++) {
            allSection[i].classList.remove("back-section");
        }


        for (let j = 0; j < totalNavList; j++) {
            if (navList[j].querySelector("a").classList.contains("active")) {
                // add back section
                addBackSectionClass(j);
            }
            navList[j].querySelector("a").classList.remove("active")
        }
        this.classList.add("active")
        showSection(this);
        if (window.innerWidth < 1200) {
            asideSectionTogglerBtn();
        }
    })

}

function removeBackSectionClass() {
    for (let i = 0; i < totalSection; i++) {
        allSection[i].classList.remove("back-section")
    }
}

function addBackSectionClass(num) {
    allSection[num].classList.add("back-section");
}

function showSection(element) {
    for (let i = 0; i < totalSection; i++) {
        allSection[i].classList.remove("active");
    }
    const target = element.getAttribute("href").split("#")[1];
    document.querySelector("#" + target).classList.add("active")

}
function updateNav(element) {
    for (let i = 0; i < totalNavList; i++) {
        navList[i].querySelector("a").classList.remove("active");
        const target = element.getAttribute("href").split("#")[1];
        if (target === navList[i].querySelector("a").getAttribute("href").split("#")[1]) {
            navList[i].querySelector("a").classList.add("active");
        }
    }
}

const navTogglerBtn = document.querySelector(".nav-toggler"),
    aside = document.querySelector(".aside");
navTogglerBtn.addEventListener("click", asideSectionTogglerBtn)
function asideSectionTogglerBtn() {
    aside.classList.toggle("open");
    navTogglerBtn.classList.toggle("open");
    for (let i = 0; i < totalSection; i++) {
        allSection[i].classList.toggle("open");
    }
}


// Blog Section
(function () {
  const blogSection = document.getElementById("blog");
  const blogContainer = document.getElementById("blog-container");
  const blogLoading = document.getElementById("blog-loading");
  const blogLightbox = document.getElementById("blog-lightbox");
  const blogLightboxInner = document.getElementById("blog-lightbox-inner");
  const blogLightboxClose = blogLightbox ? blogLightbox.querySelector(".lightbox-close") : null;
  let blogLoaded = false;

  // Fetch and render blog list when user navigates to #blog
  function loadBlogList() {
    if (blogLoaded) return;
    blogLoaded = true;

    fetch("/blog/index.html")
      .then(function (res) {
        if (!res.ok) throw new Error("Blog list not found");
        return res.text();
      })
      .then(function (html) {
        // Parse the fetched HTML and extract the blog list content
        var parser = new DOMParser();
        var doc = parser.parseFromString(html, "text/html");
        var listSection = doc.querySelector(".blog-list-section");
        if (!listSection) throw new Error("Blog list section not found");

        // Insert content
        blogContainer.innerHTML = "";
        blogContainer.appendChild(listSection);

        // Hide loading indicator
        if (blogLoading) blogLoading.style.display = "none";

        // Wire up filter buttons
        wireBlogFilters();
        // Wire up post click handlers
        wireBlogPostClicks();
      })
      .catch(function (err) {
        console.error("Failed to load blog list:", err);
        blogContainer.innerHTML =
          '<p style="text-align:center;padding:40px;color:#504e70;">加载博客列表失败，请稍后重试。</p>';
        if (blogLoading) blogLoading.style.display = "none";
      });
  }

  // Category filter
  function wireBlogFilters() {
    var filterContainer = blogContainer.querySelector(".blog-filter");
    if (!filterContainer) return;
    var filterBtns = filterContainer.children;
    var postItems = blogContainer.querySelectorAll(".blog-post-item");

    for (var i = 0; i < filterBtns.length; i++) {
      filterBtns[i].addEventListener("click", function () {
        // Update active state
        var activeBtn = filterContainer.querySelector(".active");
        if (activeBtn) activeBtn.classList.remove("active");
        this.classList.add("active");

        var filterValue = this.getAttribute("data-filter");
        for (var k = 0; k < postItems.length; k++) {
          if (filterValue === "all") {
            postItems[k].classList.remove("hide");
          } else if (postItems[k].getAttribute("data-category") === filterValue) {
            postItems[k].classList.remove("hide");
          } else {
            postItems[k].classList.add("hide");
          }
        }
      });
    }
  }

  // Post click → fetch post content → show in lightbox
  function wireBlogPostClicks() {
    var postItems = blogContainer.querySelectorAll(".blog-post-item");
    for (var i = 0; i < postItems.length; i++) {
      postItems[i].addEventListener("click", function () {
        var slug = this.getAttribute("data-slug");
        if (!slug) return;
        fetchPostContent(slug);
      });
    }
  }

  function fetchPostContent(slug) {
    blogLightboxInner.innerHTML =
      '<div class="blog-loading"><div class="loader"></div></div>';
    blogLightbox.classList.add("open");
    document.body.style.overflow = "hidden";

    fetch("/blog/posts/" + slug + ".html")
      .then(function (res) {
        if (!res.ok) throw new Error("Post not found");
        return res.text();
      })
      .then(function (html) {
        var parser = new DOMParser();
        var doc = parser.parseFromString(html, "text/html");
        var article = doc.querySelector(".blog-post-content");
        if (!article) throw new Error("Post content not found");
        blogLightboxInner.innerHTML = "";
        blogLightboxInner.appendChild(article);
      })
      .catch(function (err) {
        console.error("Failed to load post:", err);
        blogLightboxInner.innerHTML =
          '<p style="text-align:center;padding:40px;color:#504e70;">加载文章失败，请稍后重试。</p>';
      });
  }

  // Close blog lightbox
  function closeBlogLightbox() {
    blogLightbox.classList.remove("open");
    document.body.style.overflow = "";
    // Clear content after transition
    setTimeout(function () {
      blogLightboxInner.innerHTML = "";
    }, 300);
  }

  // Click close button
  if (blogLightboxClose) {
    blogLightboxClose.addEventListener("click", closeBlogLightbox);
  }

  // Click backdrop
  blogLightbox.addEventListener("click", function (event) {
    if (event.target === blogLightbox) {
      closeBlogLightbox();
    }
  });

  // ESC to close
  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape" && blogLightbox.classList.contains("open")) {
      closeBlogLightbox();
    }
  });

  // Hook into existing navigation: load blog list when #blog section becomes active
  var blogNavLink = document.querySelector('.nav a[href="#blog"]');
  if (blogNavLink) {
    blogNavLink.addEventListener("click", function () {
      setTimeout(loadBlogList, 100); // Wait for section transition
    });
  }

  // Also watch for direct URL hash changes
  window.addEventListener("hashchange", function () {
    if (window.location.hash === "#blog") {
      setTimeout(loadBlogList, 100);
    }
  });

  // Load on initial page load if hash is #blog
  if (window.location.hash === "#blog") {
    setTimeout(loadBlogList, 100);
  }

  // Load when blog section scrolls into view (mobile scroll behavior)
  if ("IntersectionObserver" in window) {
    var blogObserver = new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting) {
        loadBlogList();
        blogObserver.disconnect();
      }
    }, { rootMargin: "200px" });
    blogObserver.observe(blogSection);
  } else {
    // Fallback for older browsers
    setTimeout(loadBlogList, 500);
  }
})();