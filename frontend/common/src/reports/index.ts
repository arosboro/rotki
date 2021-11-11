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

export const Report = z.object({
  identifier: z.number(),
  name: z.string(),
  timestamp: z.union([z.number(), z.null()]),
  startTs: z.number(),
  endTs: z.number(),
  sizeOnDisk: z.union([NumericString, z.null()])
})

export const TradeHistory = z.object({
  eventsProcessed: z.number(),
  eventsLimit: z.number(),
  firstProcessedTimestamp: z.number(),
  overview: ProfitLossOverviewData,
  allEvents: z.array(ProfitLossEvent),
  loaded: z.union([z.boolean(), z.undefined()]),
})

export type TradeHistory = z.infer<typeof TradeHistory>

export type Report = z.infer<typeof Report>

export const TradeHistoryReport = TradeHistory.extend(Report.shape)

export type TradeHistoryReport = z.infer<typeof TradeHistoryReport>

export const PagedReport = PagedResourceParameters.extend(TradeHistoryReport.shape).transform(arg => {
  const pagedReport: {
    identifier?: number;
    name?: string;
    timestamp?: number | null;
    startTs?: number;
    endTs?: number;
    sizeOnDisk?: typeof NumericString | null;
    eventsProcessed?: number;
    eventsLimit?: number;
    firstProcessedTimestamp?: number
    overview: ProfitLossOverviewData,
    allEvents: ProfitLossEvent[],
    loaded?: boolean,
  } = {
    identifier: arg.identifier,
    name: arg.name,
    timestamp: arg.timestamp,
    startTs: arg.start_ts,
    endTs: arg.end_ts,
    sizeOnDisk: arg.size_on_disk,
    eventsProcessed: arg.events_processed,
    eventsLimit: arg.events_limit,
    firstProcessedTimestamp: arg.first_processed_timestamp,
    overview: arg.overview,
    allEvents: arg.all_events,
    loaded: arg.loaded
  }
  return pagedReport
})

export type PagedReport = z.infer<typeof PagedReport>

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
    entries: z.array(Report),
    entriesFound: z.number(),
    entriesLimit: z.number(),
    entriesTotal: z.union([z.number(), z.undefined()]),
}).transform(arg => {
  const reports: {
    entries?: Report[]
    entriesFound?: number;
    entriesTotal?: number;
    entriesLimit?: number;
  } = {
    entries: arg.entries,
    entriesFound: arg.entries_found,
    entriesTotal: arg.entries_total,
    entriesLimit: arg.entries_limit,
  };
  return reports;
});

export type ReportsTableData = z.infer<typeof ReportsTableData>
