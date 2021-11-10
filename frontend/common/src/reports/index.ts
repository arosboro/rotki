import { z } from "zod";
import {NumericString, PagedResourceParameters} from "../index";

export const ReportPeriod = z.object({
  start: z.number(),
  end: z.number(),
})

export type ReportPeriod = z.infer<typeof ReportPeriod>

export const ProfitLossOverviewData = z.object({
  loanProfit: NumericString,
  defiProfitLoss: NumericString,
  marginPositionsProfitLoss: NumericString,
  ledgerActionsProfitLoss: NumericString,
  settlementLosses: NumericString,
  ethereumTransactionGasCosts: NumericString,
  assetMovementFees: NumericString,
  generalTradeProfitLoss: NumericString,
  taxableTradeProfitLoss: NumericString,
  totalTaxableProfitLoss: NumericString,
  totalProfitLoss: NumericString,
})

export type ProfitLossOverviewData = z.infer<typeof ProfitLossOverviewData>

export const CostBasis = z.object({
  isComplete: z.boolean(),
  matchedAcquisitions: z.boolean(),
})

export type CostBasis = z.infer<typeof CostBasis>

export const ProfitLossEvent = z.object({
  location: z.string(),
  type: z.string(),
  paidInProfitCurrency: NumericString,
  paidAsset: z.string(),
  taxableAmount: NumericString,
  taxableBoughtCostInProfitCurrency: NumericString,
  receivedAsset: z.string(),
  taxableReceivedInProfitCurrency: NumericString,
  receivedInAsset: NumericString,
  netProfitOrLoss: NumericString,
  costBasis: z.union([CostBasis, z.null()]),
  time: z.number(),
  isVirtual: z.boolean(),
})

export type ProfitLossEvent = z.infer<typeof ProfitLossEvent>

export const ReportCacheData = z.object({
  overview: ProfitLossOverviewData,
  events: z.array(ProfitLossEvent),
  processed: z.number(),
  limit: z.number(),
  loaded: z.boolean(),
  firstProcessedTimestamp: z.number()
})

export type ReportData = z.infer<typeof ReportCacheData>

export const ReportCache = z.object({
  identifier: z.number(),
  name: z.string(),
  created: z.union([z.number(), z.null()]),
  startTs: z.number(),
  endTs: z.number(),
  sizeOnDisk: z.union([NumericString, z.null()])
})

export type ReportCache = z.infer<typeof ReportCache>

export const Report = ReportCache.extend(ReportCacheData.shape)

export type Report = z.infer<typeof Report>

export const PagedReport = PagedResourceParameters.extend(Report.shape)

export type PagedReport = z.infer<typeof PagedReport>

export const TradeHistory = z.object({
  eventsProcessed: z.number(),
  eventsLimit: z.number(),
  firstProcessedTimestamp: z.number(),
  overview: ProfitLossOverviewData,
  allEvents: z.record(z.array(ProfitLossEvent)),
})

export type TradeHistory = z.infer<typeof TradeHistory>

export const MatchedAcquisition = z.object({
  time: z.number(),
  description: z.string(),
  location: z.string(),
  usedAmount: NumericString,
  amount: NumericString,
  rate: NumericString,
  feeRate: NumericString,
})

export type MatchedAcquisition = z.infer<typeof MatchedAcquisition>

export const ReportProgress = z.object({
  processingState: z.string(),
  totalProgress: z.string()
})

export type ReportProgress = z.infer<typeof ReportProgress>

export const ReportError = z.object({
  error: z.string(),
  message: z.string(),
})

export type ReportError = z.infer<typeof ReportError>

export const ReportsTableData = PagedResourceParameters.extend({
    entries_found: z.number(),
    entries: z.array(ReportCache),
}).transform(arg => {
  const reports: {
    entriesFound?: number;
    entries?: ReportCache[]
  } = {
    entriesFound: arg.entries_found,
    entries: arg.entries
  };
  return reports;
});

export type ReportsTableData = z.infer<typeof ReportsTableData>
