import { GetterTree } from 'vuex';
import { ReportState } from '@/store/reports/types';
import { RotkehlchenState } from '@/store/types';

export const getters: GetterTree<ReportState, RotkehlchenState> = {
  reports: ({ index: { entries: reports } }: ReportState) => reports,
  overview: ({ data: { overview: overview } }: ReportState) => overview,
  events: ({ data: { allEvents: events } }: ReportState) => events,
  processed: ({ data: { eventsProcessed: processed } }: ReportState) =>
    processed,
  limit: ({ data: { eventsLimit: limit } }: ReportState) => limit,
  loaded: ({ data: { loaded: loaded } }: ReportState) => loaded,
  progress: ({ progress: { totalProgress } }: ReportState) => totalProgress,
  processingState: ({ progress: { processingState } }: ReportState) =>
    processingState
};
