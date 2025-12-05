<template>
  <canvas ref="canvasRef" @mousedown="onCanvasMouseDown" @mousemove="onCanvasMouseMove" @mouseup="onCanvasMouseUp">
    You need a browser that supports the HTML5 canvas element.
  </canvas>
</template>

<script lang="ts" setup>
import type { LineComputeInputLineCoords, LineComputeTrace } from 'src/models';

const props = defineProps<{
  uploadedImage: File | null;
  traces: LineComputeTrace[]
}>();

const inputLine = defineModel<LineComputeInputLineCoords>('inputLine', {
  required: true,
});

defineExpose({
  redrawCanvas,
});

watch(() => props.uploadedImage, () => {
  initCanvas();
});
watch([() => props.traces, inputLine.value], () => {
  redrawCanvas();
});

const canvasRef = useTemplateRef<HTMLCanvasElement>('canvasRef');

const isDrawing = ref(false);
const ctx = ref<CanvasRenderingContext2D | null>(null);

function initCanvas() {
  if (!canvasRef.value || !props.uploadedImage) return;

  const img = new Image();
  img.onload = async () => {
    await nextTick();

    if (canvasRef.value) {
      canvasRef.value.width = img.width;
      canvasRef.value.height = img.height;
    }

    ctx.value = canvasRef.value?.getContext('2d') || null;
    redrawCanvas();
  };
  img.src = URL.createObjectURL(props.uploadedImage);
};

function getCanvasCoordinates(event: MouseEvent) {
  if (!canvasRef.value) return { x: 0, y: 0 };

  const rect = canvasRef.value.getBoundingClientRect();
  const scaleX = canvasRef.value.width / rect.width;
  const scaleY = canvasRef.value.height / rect.height;

  const x = Math.round((event.clientX - rect.left) * scaleX);
  const y = Math.round((event.clientY - rect.top) * scaleY);

  return { x, y };
};

function onCanvasMouseDown(event: MouseEvent) {
  if (!canvasRef.value) return;

  const coords = getCanvasCoordinates(event);

  if (!isDrawing.value) {
    inputLine.value.startX = coords.x;
    inputLine.value.startY = coords.y;
    inputLine.value.endX = coords.x;
    inputLine.value.endY = coords.y;
    isDrawing.value = true;
  }
};

function onCanvasMouseMove(event: MouseEvent) {
  if (!canvasRef.value || !isDrawing.value) return;

  const coords = getCanvasCoordinates(event);

  inputLine.value.endX = coords.x;
  inputLine.value.endY = coords.y;
};

function onCanvasMouseUp() {
  isDrawing.value = false;
};

function redrawCanvas() {
  if (!canvasRef.value || !ctx.value || !props.uploadedImage) return;

  const img = new Image();
  img.onload = () => {
    if (ctx.value) {
      ctx.value.clearRect(0, 0, canvasRef.value!.width, canvasRef.value!.height);
      ctx.value.drawImage(img, 0, 0);
      drawLine();
      drawResults();
    }
  };
  img.src = URL.createObjectURL(props.uploadedImage);
};

function drawLine() {
  if (!ctx.value) return;

  ctx.value.beginPath();
  ctx.value.moveTo(inputLine.value.startX, inputLine.value.startY);
  ctx.value.lineTo(inputLine.value.endX, inputLine.value.endY);
  ctx.value.strokeStyle = '#aaaaaa';
  ctx.value.lineWidth = 4;
  ctx.value.setLineDash([5, 5]);
  ctx.value.stroke();

  // Draw start and end points
  ctx.value.beginPath();
  ctx.value.arc(inputLine.value.startX, inputLine.value.startY, 10, 0, 2 * Math.PI);
  ctx.value.fillStyle = '#ff0000';
  ctx.value.fill();

  ctx.value.beginPath();
  ctx.value.arc(inputLine.value.endX, inputLine.value.endY, 10, 0, 2 * Math.PI);
  ctx.value.fillStyle = '#0000ff';
  ctx.value.fill();
};

function drawResults() {
  if (!ctx.value) return;

  for (const trace of props.traces) {
    ctx.value.beginPath();
    ctx.value.strokeStyle = trace.color;
    ctx.value.lineWidth = 8;
    ctx.value.setLineDash([]);

    trace.result.path_coordinates.pixel_coordinates.forEach((point: [number, number], index: number) => {
      if (index === 0) {
        ctx.value!.moveTo(point[0], point[1]);
      } else {
        ctx.value!.lineTo(point[0], point[1]);
      }
    });

    ctx.value.stroke();
  }
};

</script>

<style scoped>

canvas {
  max-width: 500px;
  height: auto;
  border: 1px solid #ccc;
  border-radius: 8px;
}

</style>