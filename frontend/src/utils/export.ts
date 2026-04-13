import type { LineComputeTrace } from "src/models";
import Papa from "papaparse";
import jsPDF from "jspdf";
import { hslStringToRgb } from "./colors";

export function lineComputeTracesToCSV(lines: LineComputeTrace[]) {
    const data = lines.map(line => ({
        // inputs
        start_x: line.params.startX,
        start_y: line.params.startY,
        end_x: line.params.endX,
        end_y: line.params.endY,
        real_length: line.params.realLength,
        real_height: line.params.realHeight,
        interface_weight: line.params.interfaceWeight,
        boundary_margin: line.params.boundaryMargin,

        // results
        lmt_type: line.result.lmt_type,
        lmt_result: line.result.lmt_result,
        total_length: line.result.total_length,
        start_point_used_x: line.result.start_point_used[0],
        start_point_used_y: line.result.start_point_used[1],
        end_point_used_x: line.result.end_point_used[0],
        end_point_used_y: line.result.end_point_used[1],
        path: line.result.path_coordinates.pixel_coordinates.map(coord => `${coord[0]}_${coord[1]}`).join("|"),
    }));

    return Papa.unparse(data, {
        header: true,
    });
}

export function lineComputeTracesToPDF(imageDataUrl: string | null, lines: LineComputeTrace[], extractResult: (line: LineComputeTrace) => number | null = line => line.result.lmt_result) {
    const doc = new jsPDF({
        orientation: 'landscape',
    });

    const imgWidth = 150;
    const xOffset = imgWidth + 20; // Image width + some padding
    const indentedXOffset = xOffset + 5; // Further indent for details

    if (imageDataUrl) {
        doc.addImage(imageDataUrl, 'PNG', 10, 10, imgWidth, 0); // Adjust dimensions as needed
    }


    lines.forEach((line, index) => {
        let yPosition = 10 + (index) * (6 + 5 * 4 + 8); // Adjust spacing as needed
        doc.setFontSize(12);
        doc.text(`Line ${index + 1}:`, xOffset, yPosition);

        yPosition += 6;

        doc.setFillColor(...hslStringToRgb(line.color));
        doc.rect(xOffset, yPosition - 3, 3, 5 * 4, 'F');

        doc.setFontSize(10);

        doc.text(`Start: (${line.params.startX}, ${line.params.startY})`, indentedXOffset, yPosition);
        yPosition += 5;
        doc.text(`End: (${line.params.endX}, ${line.params.endY})`, indentedXOffset, yPosition);
        yPosition += 5;
        doc.text(`LMT Type: ${line.result.lmt_type}`, indentedXOffset, yPosition);
        yPosition += 5;
        const result = extractResult(line);
        doc.text(`LMT Result: ${result !== null ? result.toFixed(2) : 'N/A'}`, indentedXOffset, yPosition);

    });

    const timestamp = new Date().toISOString().replace(/:/g, '-');
    return doc.save(`line_compute_results_${timestamp}.pdf`);
}
