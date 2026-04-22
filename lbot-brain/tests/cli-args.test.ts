import { describe, expect, it } from "vitest";

import { parseCliArgs } from "../src/cli/args";

describe("parseCliArgs", () => {
  it("defaults to text mode", () => {
    expect(parseCliArgs([])).toEqual({
      mode: "text",
      help: false,
    });
  });

  it("supports --voice shortcut", () => {
    expect(parseCliArgs(["--voice"])).toEqual({
      mode: "voice",
      help: false,
    });
  });

  it("supports explicit --mode=value syntax", () => {
    expect(parseCliArgs(["--mode=voice"])).toEqual({
      mode: "voice",
      help: false,
    });
  });

  it("lets the last mode flag win", () => {
    expect(parseCliArgs(["--voice", "--text"])).toEqual({
      mode: "text",
      help: false,
    });
  });

  it("throws for missing mode value", () => {
    expect(() => parseCliArgs(["--mode"])).toThrow(
      'Missing value for --mode. Expected "text" or "voice".',
    );
  });

  it("throws for unknown arguments", () => {
    expect(() => parseCliArgs(["--wat"])).toThrow("Unknown CLI argument: --wat");
  });
});
