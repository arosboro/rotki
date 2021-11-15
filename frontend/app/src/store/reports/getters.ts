import { GetterTree } from 'vuex';
import { ReportState } from '@/store/reports/types';
import { RotkehlchenState } from '@/store/types';

export const getters: GetterTree<ReportState, RotkehlchenState> = {
  reports: ({ entries: reports }: ReportState) => reports,
  overview: ({ overview: overview }: ReportState) => overview,
  events: ({ allEvents: events }: ReportState) => events,
  processed: ({ eventsProcessed: processed }: ReportState) => processed,
  limit: ({ eventsLimit: limit }: ReportState) => limit,
  loaded: ({ loaded: loaded }: ReportState) => loaded,
  progress: ({ progress: { totalProgress } }: ReportState) => totalProgress,
  processingState: ({ progress: { processingState } }: ReportState) =>
    processingState
};
