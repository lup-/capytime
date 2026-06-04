import express from "express";
import fs from "fs";
import path from "path";

const isDev = process.env.NODE_ENV !== "production";
const API_URL = process.env.API_URL || "http://localhost:8000";
const ROOT = process.cwd();
const UPLOADS_DIR = process.env.UPLOADS_DIR || path.resolve(ROOT, "../uploads");

async function apiProxy(req, res) {
  try {
    const backendUrl = `${API_URL}${req.originalUrl}`;
    const init = {
      method: req.method,
      headers: {
        "content-type": req.headers["content-type"] || "application/json",
        ...(req.headers["authorization"] ? { authorization: req.headers["authorization"] } : {}),
      },
    };
    if (!["GET", "HEAD"].includes(req.method)) {
      init.body = JSON.stringify(req.body);
    }
    const response = await fetch(backendUrl, init);
    const body = await response.text();
    res
      .status(response.status)
      .set("content-type", response.headers.get("content-type") || "application/json")
      .send(body);
  } catch (e) {
    console.error("API proxy error:", e.message);
    res.status(502).send("Bad Gateway");
  }
}

async function start() {
  const app = express();

  app.use(express.json());

  app.get("/sitemap.xml", (req, res) => {
    const filePath = path.resolve(ROOT, "dist/client/sitemap.xml");
    if (fs.existsSync(filePath)) {
      res.type("application/xml").sendFile(filePath);
    } else {
      res.status(404).type("text/plain").send("Sitemap not found");
    }
  });

  if (isDev) {
    const { createServer: createViteServer } = await import("vite");
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "custom",
    });
    app.use(vite.middlewares);

    app.use("/api", apiProxy);

    app.get("*", async (req, res) => {
      try {
        const template = fs.readFileSync(
          path.resolve(ROOT, "index.html"),
          "utf-8",
        );
        const { render } = await vite.ssrLoadModule("/src/entry-server.ts");
        const origin = `${req.protocol}://${req.get("host")}`;
        const { html, headTags, preFetchedScript, statusCode } = await render(req.originalUrl, origin, API_URL);
        const fullHtml = template
          .replace("<!--head-tags-->", (headTags || "") + (preFetchedScript || ""))
          .replace("<!--ssr-outlet-->", html);
        res.status(statusCode ?? 200).set({ "Content-Type": "text/html" }).end(fullHtml);
      } catch (e) {
        vite.ssrFixStacktrace(e);
        console.error(e);
        res.status(500).end(e.message);
      }
    });
  } else {
    const template = fs.readFileSync(
      path.resolve(ROOT, "dist/client/index.html"),
      "utf-8",
    );
    const { render } = await import(path.resolve(ROOT, "dist/server/entry-server.js"));

    app.use("/assets", express.static(path.resolve(ROOT, "dist/client/assets")));
    app.use(express.static(path.resolve(ROOT, "dist/client"), { index: false }));
    app.use("/api", apiProxy);
    app.use("/uploads", express.static(UPLOADS_DIR));

    app.get("*", async (req, res) => {
      try {
        const origin = `${req.protocol}://${req.get("host")}`;
        const { html, headTags, preFetchedScript, statusCode } = await render(req.originalUrl, origin, API_URL);
        const fullHtml = template
          .replace("<!--head-tags-->", (headTags || "") + (preFetchedScript || ""))
          .replace("<!--ssr-outlet-->", html);
        res.status(statusCode ?? 200).set({ "Content-Type": "text/html" }).end(fullHtml);
      } catch (e) {
        console.error(e);
        res.status(500).send("Internal Server Error");
      }
    });
  }

  app.listen(3000, () => {
    console.log(`SSR server running on http://localhost:3000 (${isDev ? "dev" : "production"} mode)`);
  });
}

start();
