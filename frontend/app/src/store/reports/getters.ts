import { GetterTree } from 'vuex';
import { ReportState } from '@/store/reports/types';
import { RotkehlchenState } from '@/store/types';

export const getters: GetterTree<ReportState, RotkehlchenState> = {
  reports: ({ index: { reports: reports } }: ReportState) => reports,
  progress: ({ progress: { totalProgress } }: ReportState) => totalProgress,
  processingState: ({ progress: { processingState } }: ReportState) =>
    processingState
};
