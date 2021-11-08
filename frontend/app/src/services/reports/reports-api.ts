import { ActionResult } from '@rotki/common/lib/data';
import { ReportsTableData } from '@rotki/common/lib/reports';
import { AxiosInstance, AxiosTransformer } from 'axios';
import {
  axiosSnakeCaseTransformer,
  setupTransformer
} from '@/services/axios-tranformers';
import { handleResponse, validStatus } from '@/services/utils';

export class ReportsApi {
  private readonly axios: AxiosInstance;
  private readonly responseTransformer: AxiosTransformer[];
  private readonly requestTransformer: AxiosTransformer[];

  constructor(axios: AxiosInstance) {
    this.axios = axios;
    this.responseTransformer = axios.defaults
      .transformRequest as AxiosTransformer[];
    this.requestTransformer = [axiosSnakeCaseTransformer].concat(
      axios.defaults.transformRequest as AxiosTransformer[]
    );
  }

  fetchReports(page: number, rows: number): Promise<ReportsTableData> {
    return this.axios
      .get<ActionResult<ReportsTableData>>('/reports', {
        params: { page, rows },
        validateStatus: validStatus,
        transformResponse: setupTransformer([])
      })
      .then(handleResponse)
      .then(result => result.parse(result));
  }
}
