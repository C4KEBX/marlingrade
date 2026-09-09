import { describe, it, expect, vi, beforeEach } from "vitest";
import { loadZips, loadParcels, _resetCache } from "./bundle";
import zipsFx from "../test/fixtures/zips.json";
import parcelsFx from "../test/fixtures/parcels-78749.json";

beforeEach(() => { _resetCache(); vi.restoreAllMocks(); });

describe("bundle loader", () => {
  it("parses zips.json into ZipRecord[]", async () => {
    vi.spyOn(global, "fetch").mockResolvedValue(
      new Response(JSON.stringify(zipsFx), { status: 200 }),
    );
    const zips = await loadZips();
    expect(zips.find((z) => z.zip === "78749")?.distribution.A).toBeDefined();
  });

  it("memoises parcels per zip (one fetch for two calls)", async () => {
    const spy = vi.spyOn(global, "fetch").mockResolvedValue(
      new Response(JSON.stringify(parcelsFx), { status: 200 }),
    );
    await loadParcels("78749");
    await loadParcels("78749");
    expect(spy).toHaveBeenCalledTimes(1);
  });
});
