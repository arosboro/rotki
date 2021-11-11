import { ActionResult } from '@rotki/common/lib/data';
import { PagedReport, ReportsTableData } from '@rotki/common/lib/reports';
import { AxiosInstance, AxiosTransformer } from 'axios';
import {
  axiosSnakeCaseTransformer,
  setupTransformer
} from '@/services/axios-tranformers';
import { reportNumericKeys } from '@/services/reports/const';
import { handleResponse, validStatus } from '@/services/utils';

export class ReportsApi {
  private readonly axios: AxiosInstance;
  private readonly responseTransformer: AxiosTransformer[] =
    setupTransformer(reportNumericKeys);
  private readonly requestTransformer: AxiosTransformer[];

  constructor(axios: AxiosInstance) {
    this.axios = axios;
    this.responseTransformer = axios.defaults
      .transformRequest as AxiosTransformer[];
    this.requestTransformer = [axiosSnakeCaseTransformer].concat(
      axios.defaults.transformRequest as AxiosTransformer[]
    );
  }

  fetchReports(): Promise<ReportsTableData> {
    return this.axios
      .get<ActionResult<ReportsTableData>>('/reports', {
        validateStatus: validStatus,
        transformResponse: setupTransformer(reportNumericKeys)
      })
      .then(handleResponse)
      .then(result => ReportsTableData.parse(result));
  }

  fetchReport(report_id: number): Promise<PagedReport> {
    return this.axios
      .get<ActionResult<PagedReport>>('/reports', {
        params: { report_id },
        validateStatus: validStatus,
        transformResponse: setupTransformer(reportNumericKeys)
      })
      .then(handleResponse)
      .then(result => PagedReport.parse(result));
  }
}
