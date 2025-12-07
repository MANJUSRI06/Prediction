import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { Document, Packer, Paragraph, Table, TableCell, TableRow, TextRun, HeadingLevel, BorderStyle, WidthType, AlignmentType } from 'docx';
import { saveAs } from 'file-saver';
import { NewCropResultData } from '@/components/AgriCare/NewCropResults';
import { ExistingCropResultData } from '@/components/AgriCare/ExistingCropResults';

/**
 * Generate PDF report from HTML element
 */
export const generatePDFFromHTML = async (
  elementId: string,
  fileName: string
): Promise<void> => {
  try {
    const element = document.getElementById(elementId);
    if (!element) {
      throw new Error(`Element with id ${elementId} not found`);
    }

    const canvas = await html2canvas(element, {
      scale: 2,
      backgroundColor: '#ffffff',
    });

    const imgData = canvas.toDataURL('image/png');
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4',
    });

    const pageWidth = pdf.internal.pageSize.getWidth();
    const pageHeight = pdf.internal.pageSize.getHeight();
    const imgWidth = pageWidth - 20;
    const imgHeight = (canvas.height * imgWidth) / canvas.width;

    let heightLeft = imgHeight;
    let position = 10;

    pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
    heightLeft -= pageHeight - 20;

    while (heightLeft > 0) {
      position = heightLeft - imgHeight + 10;
      pdf.addPage();
      pdf.addImage(imgData, 'PNG', 10, position, imgWidth, imgHeight);
      heightLeft -= pageHeight - 20;
    }

    pdf.save(fileName);
  } catch (error) {
    console.error('Error generating PDF:', error);
    throw error;
  }
};

/**
 * Generate DOCX report for New Crop Prediction
 */
export const generateNewCropReportDOCX = async (
  data: NewCropResultData,
  farmSize: number,
  fileName: string
): Promise<void> => {
  try {
    const doc = new Document({
      sections: [
        {
          children: [
            new Paragraph({
              text: 'CROP YIELD PREDICTION REPORT',
              heading: HeadingLevel.HEADING_1,
              bold: true,
              fontSize: 24,
            }),
            new Paragraph({
              text: `Generated on ${new Date().toLocaleDateString()}`,
              fontSize: 10,
              color: '666666',
            }),
            new Paragraph({ text: '' }),

            // Yield Prediction Section
            new Paragraph({
              text: 'Predicted Yield',
              heading: HeadingLevel.HEADING_2,
              bold: true,
              fontSize: 14,
            }),
            new Paragraph({
              text: `Success Rate: ${data.predictedYieldPct}%`,
              fontSize: 11,
              margin: { bottom: 100 },
            }),
            new Paragraph({
              text: `Per Acre: ${data.predictedYieldQtyPerAcre} quintals`,
              fontSize: 11,
              margin: { bottom: 100 },
            }),
            new Paragraph({
              text: `Total for ${farmSize} acres: ${data.totalYield} quintals`,
              fontSize: 11,
              bold: true,
              margin: { bottom: 200 },
            }),

            // Weather Recommendation
            new Paragraph({
              text: 'Weather Recommendation',
              heading: HeadingLevel.HEADING_2,
              bold: true,
              fontSize: 14,
            }),
            new Paragraph({
              text: data.weatherRecommendation,
              fontSize: 11,
              margin: { bottom: 100 },
            }),
            new Paragraph({
              text: `Risk Level: ${data.weatherRisk.toUpperCase()}`,
              fontSize: 11,
              margin: { bottom: 200 },
            }),

            // Soil Suggestions
            new Paragraph({
              text: 'Soil Health Suggestions',
              heading: HeadingLevel.HEADING_2,
              bold: true,
              fontSize: 14,
            }),
            new Table({
              width: { size: 100, type: WidthType.PERCENTAGE },
              rows: [
                new TableRow({
                  children: [
                    new TableCell({
                      children: [new Paragraph({ text: 'Nutrient', bold: true })],
                      borders: { top: { style: BorderStyle.SINGLE, size: 6 }, bottom: { style: BorderStyle.SINGLE, size: 6 } },
                    }),
                    new TableCell({
                      children: [new Paragraph({ text: 'Value', bold: true })],
                      borders: { top: { style: BorderStyle.SINGLE, size: 6 }, bottom: { style: BorderStyle.SINGLE, size: 6 } },
                    }),
                    new TableCell({
                      children: [new Paragraph({ text: 'Status', bold: true })],
                      borders: { top: { style: BorderStyle.SINGLE, size: 6 }, bottom: { style: BorderStyle.SINGLE, size: 6 } },
                    }),
                  ],
                }),
                ...Object.entries(data.soilSuggestions).map(
                  ([key, item]) =>
                    new TableRow({
                      children: [
                        new TableCell({
                          children: [new Paragraph({ text: key.toUpperCase() })],
                        }),
                        new TableCell({
                          children: [new Paragraph({ text: `${item.value}` })],
                        }),
                        new TableCell({
                          children: [new Paragraph({ text: item.status })],
                        }),
                      ],
                    })
                ),
              ],
              margin: { bottom: 200 },
            }),

            // Irrigation Schedule
            new Paragraph({
              text: 'Irrigation Schedule',
              heading: HeadingLevel.HEADING_2,
              bold: true,
              fontSize: 14,
            }),
            new Paragraph({
              text: `Current Week's Focus: ${data.irrigationAlert}`,
              fontSize: 11,
              margin: { bottom: 100 },
            }),
            new Table({
              width: { size: 100, type: WidthType.PERCENTAGE },
              rows: [
                new TableRow({
                  children: [
                    new TableCell({
                      children: [new Paragraph({ text: 'Day', bold: true })],
                      borders: { top: { style: BorderStyle.SINGLE, size: 6 }, bottom: { style: BorderStyle.SINGLE, size: 6 } },
                    }),
                    new TableCell({
                      children: [new Paragraph({ text: 'Amount', bold: true })],
                      borders: { top: { style: BorderStyle.SINGLE, size: 6 }, bottom: { style: BorderStyle.SINGLE, size: 6 } },
                    }),
                    new TableCell({
                      children: [new Paragraph({ text: 'Weather', bold: true })],
                      borders: { top: { style: BorderStyle.SINGLE, size: 6 }, bottom: { style: BorderStyle.SINGLE, size: 6 } },
                    }),
                  ],
                }),
                ...data.irrigationSchedule.map(
                  (item) =>
                    new TableRow({
                      children: [
                        new TableCell({
                          children: [new Paragraph({ text: item.day })],
                        }),
                        new TableCell({
                          children: [new Paragraph({ text: item.amount })],
                        }),
                        new TableCell({
                          children: [new Paragraph({ text: item.weather })],
                        }),
                      ],
                    })
                ),
              ],
              margin: { bottom: 200 },
            }),

            // Fertilizer Recommendation
            new Paragraph({
              text: 'Fertilizer Recommendation',
              heading: HeadingLevel.HEADING_2,
              bold: true,
              fontSize: 14,
            }),
            new Paragraph({
              text: `NPK Ratio: ${data.fertilizerRecommendation.ratio}`,
              fontSize: 11,
              bold: true,
              margin: { bottom: 100 },
            }),
            new Paragraph({
              text: `Important: ${data.fertilizerRecommendation.important}`,
              fontSize: 11,
              margin: { bottom: 150 },
            }),
            new Paragraph({
              text: 'Application Splits:',
              fontSize: 11,
              bold: true,
              margin: { bottom: 100 },
            }),
            ...data.fertilizerRecommendation.splits.map(
              (split) =>
                new Paragraph({
                  text: `${split.stage} (Day ${split.day}): ${split.fertilizer}`,
                  fontSize: 11,
                  margin: { bottom: 50 },
                })
            ),

            new Paragraph({ text: '' }),

            // Pest Risk
            new Paragraph({
              text: 'Pest Risk Assessment',
              heading: HeadingLevel.HEADING_2,
              bold: true,
              fontSize: 14,
            }),
            ...data.pestRisks.map(
              (pest) =>
                new Paragraph({
                  text: `${pest.name}: ${pest.level.toUpperCase()}`,
                  fontSize: 11,
                  margin: { bottom: 50 },
                })
            ),

            new Paragraph({ text: '' }),

            // Cost & Profit
            new Paragraph({
              text: 'Cost & Profit Estimate (per acre)',
              heading: HeadingLevel.HEADING_2,
              bold: true,
              fontSize: 14,
            }),
            new Paragraph({
              text: `Cost: ₹${data.costProfit.costPerAcre.toLocaleString()}`,
              fontSize: 11,
              margin: { bottom: 100 },
            }),
            new Paragraph({
              text: `Revenue: ₹${data.costProfit.revenuePerAcre.toLocaleString()}`,
              fontSize: 11,
              margin: { bottom: 100 },
            }),
            new Paragraph({
              text: `Profit: ₹${data.costProfit.profitPerAcre.toLocaleString()}`,
              fontSize: 11,
              bold: true,
              margin: { bottom: 200 },
            }),

            // Season Comparison
            new Paragraph({
              text: 'Season Comparison',
              heading: HeadingLevel.HEADING_2,
              bold: true,
              fontSize: 14,
            }),
            new Paragraph({
              text: `${data.seasonComparison.trend.toUpperCase()} by ${Math.abs(data.seasonComparison.changePercent)}% compared to previous seasons`,
              fontSize: 11,
              margin: { bottom: 200 },
            }),

            // Footer
            new Paragraph({
              text: 'AgriCare — Empowering Odisha Farmers with AI-powered Crop Intelligence',
              fontSize: 9,
              color: '666666',
              alignment: AlignmentType.CENTER,
            }),
          ],
        },
      ],
    });

    Packer.toBlob(doc).then((blob) => {
      saveAs(blob, fileName);
    });
  } catch (error) {
    console.error('Error generating DOCX:', error);
    throw error;
  }
};

/**
 * Generate DOCX report for Existing Crop Diagnosis
 */
export const generateExistingCropReportDOCX = async (
  data: ExistingCropResultData,
  fileName: string
): Promise<void> => {
  try {
    const doc = new Document({
      sections: [
        {
          children: [
            new Paragraph({
              text: 'CROP DIAGNOSIS REPORT',
              heading: HeadingLevel.HEADING_1,
              bold: true,
              fontSize: 24,
            }),
            new Paragraph({
              text: `Generated on ${new Date().toLocaleDateString()}`,
              fontSize: 10,
              color: '666666',
            }),
            new Paragraph({ text: '' }),

            // Diagnosed Issue
            new Paragraph({
              text: 'Diagnosed Issue',
              heading: HeadingLevel.HEADING_2,
              bold: true,
              fontSize: 14,
            }),
            new Paragraph({
              text: data.diagnosedIssue,
              fontSize: 11,
              bold: true,
              margin: { bottom: 100 },
            }),
            new Paragraph({
              text: `Confidence: ${data.issueConfidence}%`,
              fontSize: 11,
              margin: { bottom: 200 },
            }),

            // Detection Analysis
            new Paragraph({
              text: 'Detection Analysis',
              heading: HeadingLevel.HEADING_2,
              bold: true,
              fontSize: 14,
            }),
            new Paragraph({
              text: data.imageProcessingLog,
              fontSize: 11,
              margin: { bottom: 200 },
            }),

            // Soil Analysis
            new Paragraph({
              text: 'Soil Analysis',
              heading: HeadingLevel.HEADING_2,
              bold: true,
              fontSize: 14,
            }),
            new Paragraph({
              text: `Inferred Soil Type: ${data.soilTypeFromImage}`,
              fontSize: 11,
              margin: { bottom: 100 },
            }),
            new Paragraph({
              text: `Recommended Crops for this Soil: ${data.recommendedCropForSoil.join(', ')}`,
              fontSize: 11,
              margin: { bottom: 200 },
            }),

            // Remedial Actions
            new Paragraph({
              text: 'Remedial Actions',
              heading: HeadingLevel.HEADING_2,
              bold: true,
              fontSize: 14,
            }),
            ...data.remedialActions.map(
              (action, index) =>
                new Paragraph({
                  text: `${index + 1}. ${action}`,
                  fontSize: 11,
                  margin: { bottom: 100 },
                })
            ),

            new Paragraph({ text: '' }),

            // Irrigation Adjustments
            new Paragraph({
              text: 'Irrigation Adjustments',
              heading: HeadingLevel.HEADING_2,
              bold: true,
              fontSize: 14,
            }),
            ...data.irrigationAdjustments.map(
              (adjustment) =>
                new Paragraph({
                  text: `• ${adjustment}`,
                  fontSize: 11,
                  margin: { bottom: 50 },
                })
            ),

            new Paragraph({ text: '' }),

            // Growth Stage
            new Paragraph({
              text: 'Growth Stage',
              heading: HeadingLevel.HEADING_2,
              bold: true,
              fontSize: 14,
            }),
            new Paragraph({
              text: `Current Stage: ${data.growthStageExisting.currentStage}`,
              fontSize: 11,
              margin: { bottom: 100 },
            }),
            new Paragraph({
              text: `Days to Next Stage: ${data.growthStageExisting.daysToNextStage}`,
              fontSize: 11,
              margin: { bottom: 100 },
            }),
            new Paragraph({
              text: `Next Stage: ${data.growthStageExisting.nextStage}`,
              fontSize: 11,
              margin: { bottom: 200 },
            }),

            // Cost Impact Estimate
            new Paragraph({
              text: 'Cost Impact Estimate',
              heading: HeadingLevel.HEADING_2,
              bold: true,
              fontSize: 14,
            }),
            new Paragraph({
              text: `If Unresolved: -₹${data.costAdjustmentEstimate.unresolvedLoss.toLocaleString()} (potential loss)`,
              fontSize: 11,
              margin: { bottom: 100 },
            }),
            new Paragraph({
              text: `If Resolved: +₹${data.costAdjustmentEstimate.resolvedGain.toLocaleString()} (potential gain)`,
              fontSize: 11,
              bold: true,
              margin: { bottom: 200 },
            }),

            // Season Comparison
            new Paragraph({
              text: 'Season/Field Comparison',
              heading: HeadingLevel.HEADING_2,
              bold: true,
              fontSize: 14,
            }),
            new Paragraph({
              text: data.historyComparison,
              fontSize: 11,
              margin: { bottom: 200 },
            }),

            // Footer
            new Paragraph({
              text: 'AgriCare — Empowering Odisha Farmers with AI-powered Crop Intelligence',
              fontSize: 9,
              color: '666666',
              alignment: AlignmentType.CENTER,
            }),
          ],
        },
      ],
    });

    Packer.toBlob(doc).then((blob) => {
      saveAs(blob, fileName);
    });
  } catch (error) {
    console.error('Error generating DOCX:', error);
    throw error;
  }
};

/**
 * Generate PDF report for New Crop Prediction
 */
export const generateNewCropReportPDF = async (
  data: NewCropResultData,
  farmSize: number,
  fileName: string
): Promise<void> => {
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
  });

  let yPosition = 20;
  const pageWidth = pdf.internal.pageSize.getWidth();
  const margin = 15;
  const contentWidth = pageWidth - 2 * margin;

  const addHeading = (text: string) => {
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text(text, margin, yPosition);
    yPosition += 10;
  };

  const addSubHeading = (text: string) => {
    pdf.setFontSize(11);
    pdf.setFont(undefined, 'bold');
    pdf.text(text, margin, yPosition);
    yPosition += 7;
  };

  const addText = (text: string, fontSize: number = 10) => {
    pdf.setFontSize(fontSize);
    pdf.setFont(undefined, 'normal');
    const lines = pdf.splitTextToSize(text, contentWidth);
    lines.forEach((line: string) => {
      if (yPosition > 280) {
        pdf.addPage();
        yPosition = 20;
      }
      pdf.text(line, margin, yPosition);
      yPosition += 6;
    });
  };

  const checkPageBreak = () => {
    if (yPosition > 280) {
      pdf.addPage();
      yPosition = 20;
    }
  };

  // Title
  pdf.setFontSize(18);
  pdf.setFont(undefined, 'bold');
  pdf.text('CROP YIELD PREDICTION REPORT', margin, yPosition);
  yPosition += 12;

  addText(`Generated on ${new Date().toLocaleDateString()}`);
  yPosition += 5;

  // Yield Prediction
  checkPageBreak();
  addHeading('Predicted Yield');
  addText(`Success Rate: ${data.predictedYieldPct}%`);
  addText(`Per Acre: ${data.predictedYieldQtyPerAcre} quintals`);
  addText(`Total for ${farmSize} acres: ${data.totalYield} quintals`);
  yPosition += 5;

  // Weather
  checkPageBreak();
  addHeading('Weather Recommendation');
  addText(data.weatherRecommendation);
  addText(`Risk Level: ${data.weatherRisk.toUpperCase()}`);
  yPosition += 5;

  // Soil Suggestions
  checkPageBreak();
  addHeading('Soil Health Suggestions');
  Object.entries(data.soilSuggestions).forEach(([key, item]) => {
    addText(`${key.toUpperCase()}: ${item.value} - ${item.status}`);
    addText(`  → ${item.suggestion}`);
  });
  yPosition += 5;

  // Irrigation Schedule
  checkPageBreak();
  addHeading('Irrigation Schedule');
  addText(`Current Week's Focus: ${data.irrigationAlert}`);
  data.irrigationSchedule.forEach((item) => {
    addText(`${item.day}: ${item.amount} (${item.weather})`);
  });
  yPosition += 5;

  // Fertilizer
  checkPageBreak();
  addHeading('Fertilizer Recommendation');
  addText(`NPK Ratio: ${data.fertilizerRecommendation.ratio}`);
  addText(`Important: ${data.fertilizerRecommendation.important}`);
  addSubHeading('Application Splits:');
  data.fertilizerRecommendation.splits.forEach((split) => {
    addText(`${split.stage} (Day ${split.day}): ${split.fertilizer}`);
  });
  yPosition += 5;

  // Pest Risk
  checkPageBreak();
  addHeading('Pest Risk Assessment');
  data.pestRisks.forEach((pest) => {
    addText(`${pest.name}: ${pest.level.toUpperCase()}`);
  });
  yPosition += 5;

  // Cost & Profit
  checkPageBreak();
  addHeading('Cost & Profit Estimate (per acre)');
  addText(`Cost: ₹${data.costProfit.costPerAcre.toLocaleString()}`);
  addText(`Revenue: ₹${data.costProfit.revenuePerAcre.toLocaleString()}`);
  addText(`Profit: ₹${data.costProfit.profitPerAcre.toLocaleString()}`);
  yPosition += 5;

  // Season Comparison
  checkPageBreak();
  addHeading('Season Comparison');
  addText(`${data.seasonComparison.trend.toUpperCase()} by ${Math.abs(data.seasonComparison.changePercent)}% compared to previous seasons`);
  yPosition += 10;

  // Footer
  pdf.setFontSize(8);
  pdf.setFont(undefined, 'normal');
  pdf.text('AgriCare — Empowering Odisha Farmers with AI-powered Crop Intelligence', margin, pdf.internal.pageSize.getHeight() - 10);

  pdf.save(fileName);
};

/**
 * Generate PDF report for Existing Crop Diagnosis
 */
export const generateExistingCropReportPDF = async (
  data: ExistingCropResultData,
  fileName: string
): Promise<void> => {
  const pdf = new jsPDF({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
  });

  let yPosition = 20;
  const pageWidth = pdf.internal.pageSize.getWidth();
  const margin = 15;
  const contentWidth = pageWidth - 2 * margin;

  const addHeading = (text: string) => {
    pdf.setFontSize(14);
    pdf.setFont(undefined, 'bold');
    pdf.text(text, margin, yPosition);
    yPosition += 10;
  };

  const addText = (text: string, fontSize: number = 10) => {
    pdf.setFontSize(fontSize);
    pdf.setFont(undefined, 'normal');
    const lines = pdf.splitTextToSize(text, contentWidth);
    lines.forEach((line: string) => {
      if (yPosition > 280) {
        pdf.addPage();
        yPosition = 20;
      }
      pdf.text(line, margin, yPosition);
      yPosition += 6;
    });
  };

  const checkPageBreak = () => {
    if (yPosition > 280) {
      pdf.addPage();
      yPosition = 20;
    }
  };

  // Title
  pdf.setFontSize(18);
  pdf.setFont(undefined, 'bold');
  pdf.text('CROP DIAGNOSIS REPORT', margin, yPosition);
  yPosition += 12;

  addText(`Generated on ${new Date().toLocaleDateString()}`);
  yPosition += 5;

  // Diagnosed Issue
  checkPageBreak();
  addHeading('Diagnosed Issue');
  addText(data.diagnosedIssue);
  addText(`Confidence: ${data.issueConfidence}%`);
  yPosition += 5;

  // Detection Analysis
  checkPageBreak();
  addHeading('Detection Analysis');
  addText(data.imageProcessingLog);
  yPosition += 5;

  // Soil Analysis
  checkPageBreak();
  addHeading('Soil Analysis');
  addText(`Inferred Soil Type: ${data.soilTypeFromImage}`);
  addText(`Recommended Crops: ${data.recommendedCropForSoil.join(', ')}`);
  yPosition += 5;

  // Remedial Actions
  checkPageBreak();
  addHeading('Remedial Actions');
  data.remedialActions.forEach((action, index) => {
    addText(`${index + 1}. ${action}`);
  });
  yPosition += 5;

  // Irrigation Adjustments
  checkPageBreak();
  addHeading('Irrigation Adjustments');
  data.irrigationAdjustments.forEach((adjustment) => {
    addText(`• ${adjustment}`);
  });
  yPosition += 5;

  // Growth Stage
  checkPageBreak();
  addHeading('Growth Stage');
  addText(`Current Stage: ${data.growthStageExisting.currentStage}`);
  addText(`Days to Next Stage: ${data.growthStageExisting.daysToNextStage}`);
  addText(`Next Stage: ${data.growthStageExisting.nextStage}`);
  yPosition += 5;

  // Cost Impact
  checkPageBreak();
  addHeading('Cost Impact Estimate');
  addText(`If Unresolved: -₹${data.costAdjustmentEstimate.unresolvedLoss.toLocaleString()} (potential loss)`);
  addText(`If Resolved: +₹${data.costAdjustmentEstimate.resolvedGain.toLocaleString()} (potential gain)`);
  yPosition += 5;

  // Season Comparison
  checkPageBreak();
  addHeading('Season/Field Comparison');
  addText(data.historyComparison);
  yPosition += 10;

  // Footer
  pdf.setFontSize(8);
  pdf.setFont(undefined, 'normal');
  pdf.text('AgriCare — Empowering Odisha Farmers with AI-powered Crop Intelligence', margin, pdf.internal.pageSize.getHeight() - 10);

  pdf.save(fileName);
};
