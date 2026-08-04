module.exports = {
  layout: "post.njk",
  tags: ["post"],
  eleventyComputed: {
    permalink: function (data) {
      // If page already declares its own permalink, use it
      if (data.permalink) return data.permalink;
      return `/posts/${data.page.fileSlug}.html`;
    },
    summary: function (data) {
      // Extract summary from raw markdown content (before layout wrapping)
      var raw = data.page.rawInput || "";
      // Strip YAML frontmatter (everything between first two ---)
      raw = raw.replace(/^---[\s\S]*?---\s*/, "");
      // Strip markdown headings, links, images, code blocks, and HTML tags
      raw = raw
        .replace(/#{1,6}\s+/g, "")
        .replace(/\[([^\]]*)\]\([^)]*\)/g, "$1")
        .replace(/!\[[^\]]*\]\([^)]*\)/g, "")
        .replace(/```[\s\S]*?```/g, "")
        .replace(/`([^`]*)`/g, "$1")
        .replace(/<[^>]*>/g, "")
        .replace(/\n+/g, " ")
        .trim();
      return raw.length > 120 ? raw.substring(0, 120) + "..." : raw;
    },
  },
};