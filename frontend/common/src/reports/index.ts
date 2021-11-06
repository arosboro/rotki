import { z } from "zod";
import {NumericString, ResourcePager} from "../index";

const HistoryReport = z.object({
    identifier: z.number(),
    name: z.string(),
    created: z.number(),
    start_ts: z.number(),
    end_ts: z.number(),
    size_on_disk: NumericString,
})

export type HistoryReport = z.infer<typeof HistoryReport>

export const HistoryReports = z.record(z.array(HistoryReport))

export type HistoryReports = z.infer<typeof HistoryReports>

export const HistoryReportsPaginated = ResourcePager.extend({
    reports: HistoryReports,
})

export type HistoryReportsPaginated = z.infer<typeof HistoryReportsPaginated>
