import { z } from "zod";
import {NumericString, PagedResource} from "../index";

const ReportPeriod = z.object({
  start: z.number(),
  end: z.number(),
})

export type ReportPeriod = z.infer<typeof ReportPeriod>

const ProfitLossOverviewData = z.object({
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

const CostBasis = z.object({
  isComplete: z.boolean(),
  matchedAcquisitions: z.boolean(),
})

export type CostBasis = z.infer<typeof CostBasis>

const ProfitLossEvent = z.object({
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

const ReportCacheData = z.object({
  overview: ProfitLossOverviewData,
  events: z.array(ProfitLossEvent),
  processed: z.number(),
  limit: z.number(),
  loaded: z.boolean(),
  firstProcessedTimestamp: z.number()
})

export type ReportData = z.infer<typeof ReportCacheData>

const ReportCache = z.object({
  identifier: z.number(),
  name: z.string(),
  created: z.number(),
  start: z.number(),
  end: z.number(),
  sizeOnDisk: NumericString,
})

export type ReportCache = z.infer<typeof ReportCache>

const Report = ReportCache.extend(ReportCacheData.shape)

export type Report = z.infer<typeof Report>

const PagedReport = PagedResource.extend(Report.shape)

export type PagedReport = z.infer<typeof PagedReport>

const TradeHistory = z.object({
  eventsProcessed: z.number(),
  eventsLimit: z.number(),
  firstProcessedTimestamp: z.number(),
  overview: ProfitLossOverviewData,
  allEvents: z.record(z.array(ProfitLossEvent)),
})

export type TradeHistory = z.infer<typeof TradeHistory>

const MatchedAcquisition = z.object({
  time: z.number(),
  description: z.string(),
  location: z.string(),
  usedAmount: NumericString,
  amount: NumericString,
  rate: NumericString,
  feeRate: NumericString,
})

export type MatchedAcquisition = z.infer<typeof MatchedAcquisition>

const ReportProgress = z.object({
  processingState: z.string(),
  totalProgress: z.string()
})

export type ReportProgress = z.infer<typeof ReportProgress>

const ReportError = z.object({
  error: z.string(),
  message: z.string(),
})

export type ReportError = z.infer<typeof ReportError>

const ReportsTableData = PagedResource.extend({
    reports: z.array(ReportCache),
})

export type ReportsTableData = z.infer<typeof ReportsTableData>
