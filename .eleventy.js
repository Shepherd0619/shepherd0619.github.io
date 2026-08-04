module.exports = function (eleventyConfig) {
  // Input: blog directory (markdown posts)
  // Output: same blog directory (generated HTML lives alongside source)
  eleventyConfig.addFilter("dateString", function (date) {
    if (!date) return "";
    const d = new Date(date);
    const y = d.getFullYear();
    const m = String(d.getMonth() + 1).padStart(2, "0");
    const day = String(d.getDate()).padStart(2, "0");
    return `${y}-${m}-${day}`;
  });

  eleventyConfig.addFilter("truncate", function (str, len) {
    if (!str) return "";
    return str.length > len ? str.substring(0, len) + "..." : str;
  });

  eleventyConfig.addFilter("categoryClass", function (cat) {
    if (!cat) return "";
    // Map Chinese category names to CSS-safe class names
    var map = {
      "IT 运维": "it-运维",
      "Unity 开发": "unity-开发",
      "Windows Server": "windows-server",
      "其他": "其他"
    };
    return map[cat] || cat.toLowerCase().replace(/\s+/g, "-");
  });

  eleventyConfig.addFilter("reverse", function (arr) {
    if (!Array.isArray(arr)) return arr;
    return arr.slice().reverse();
  });

  eleventyConfig.addFilter("striptags", function (str) {
    if (!str) return "";
    return str.replace(/<[^>]*>/g, "");
  });

  // Passthrough copy not needed: input=output=blog, images already in place

  // Rewrite relative image paths to absolute: images/x.png → /blog/images/x.png
  // Needed because post HTML at /blog/posts/ would resolve images/ relative to /blog/posts/
  eleventyConfig.addTransform("fixImagePaths", function (content) {
    if (!this.outputPath || !this.outputPath.endsWith(".html")) return content;
    return content.replace(/(src|href)="images\//g, '$1="/blog/images/');
  });

  eleventyConfig.addCollection("postsIndex", function (collectionApi) {
    return collectionApi.getFilteredByTag("post").map(function (post) {
      return {
        title: post.data.title,
        slug: post.fileSlug,
        date: post.data.date,
        categories: post.data.categories,
        tags: post.data.tags,
        source: post.data.source,
        summary: post.data.summary || "",
      };
    });
  });

  return {
    dir: {
      input: "blog",
      output: "blog",
      includes: "../_include",
      layouts: "../_include/layouts",
      data: ".",
    },
    markdownTemplateEngine: "njk",
    htmlTemplateEngine: "njk",
  };
};
