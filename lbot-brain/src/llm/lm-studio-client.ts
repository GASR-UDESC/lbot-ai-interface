export interface LlmTextContentPart {
  type: "text";
  text: string;
}

export interface LlmImageContentPart {
  type: "image_url";
  image_url: {
    url: string;
    detail?: "auto" | "low" | "high";
  };
}

export type LlmContentPart = LlmTextContentPart | LlmImageContentPart;

export interface LlmMessage {
  role: "system" | "user" | "assistant";
  content: string | LlmContentPart[];
}

export interface LmStudioClientConfig {
  baseURL: string;
  apiKey: string;
  model: string;
  temperature: number;
  maxTokens: number;
}

export interface JsonSchemaConfig {
  name: string;
  schema: object;
  strict?: boolean;
}

interface LlmResponseContentPart {
  type?: string;
  text?: string | { value?: string };
}

function contentToString(content: string | null | LlmResponseContentPart[]): string {
  if (typeof content === "string") {
    return content;
  }

  if (!content) {
    return "";
  }

  return content
    .map((part) => {
      if (typeof part.text === "string") {
        return part.text;
      }

      if (part.text && typeof part.text.value === "string") {
        return part.text.value;
      }

      return "";
    })
    .join("\n")
    .trim();
}

export class LmStudioHttpError extends Error {
  constructor(
    public readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "LmStudioHttpError";
  }
}

export class LmStudioClient {
  constructor(private readonly config: LmStudioClientConfig) {}

  async generate(
    messages: LlmMessage[],
    options?: {
      jsonSchema?: JsonSchemaConfig;
    },
  ): Promise<string> {
    const requestBody: Record<string, unknown> = {
      model: this.config.model,
      messages,
      temperature: this.config.temperature,
      max_tokens: this.config.maxTokens,
    };

    if (options?.jsonSchema) {
      requestBody.response_format = {
        type: "json_schema",
        json_schema: {
          name: options.jsonSchema.name,
          strict: options.jsonSchema.strict ?? true,
          schema: options.jsonSchema.schema,
        },
      };
    }

    const response = await fetch(`${this.config.baseURL}/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${this.config.apiKey}`,
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new LmStudioHttpError(
        response.status,
        `LM Studio request failed (${response.status}): ${errorText}`,
      );
    }

    const payload = (await response.json()) as {
      choices?: Array<{
        message?: {
          content?: string | null | LlmResponseContentPart[];
        };
      }>;
    };

    const content = contentToString(payload.choices?.[0]?.message?.content ?? null);

    if (!content) {
      throw new Error("LM Studio returned an empty response.");
    }

    return content;
  }
}
