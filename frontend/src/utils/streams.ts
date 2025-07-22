/**
 * A TransformStream that limits the amount of data that can be written to it.
 */
export class LimitedTransformStream extends TransformStream {
  constructor(limit = 10000) {
      let bytesWritten = 0;

      super({
          transform(chunk, controller) {
              // Track how much data has been written
              const chunkLength = chunk.length || chunk.byteLength;
              if (bytesWritten + chunkLength > limit) {
                  const remainingBytes = limit - bytesWritten;
                  if (remainingBytes > 0) {
                      // Write only the remaining allowed bytes
                      controller.enqueue(chunk.slice(0, remainingBytes));
                      bytesWritten += remainingBytes;
                  }
                  // Ignore the rest of the stream since the limit is reached
              } else {
                  // If under the limit, write the full chunk
                  controller.enqueue(chunk);
                  bytesWritten += chunkLength;
              }
          },
      });
  }
}