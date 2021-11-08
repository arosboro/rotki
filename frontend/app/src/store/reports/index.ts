import { Module } from 'vuex';
import { RotkehlchenState } from '@/store/types';
import { actions } from './actions';
import { getters } from './getters';
import { mutations } from './mutations';
import { state } from './state';
import { ReportState } from './types';

const namespaced: boolean = true;

export const reports: Module<ReportState, RotkehlchenState> = {
  namespaced,
  mutations,
  actions,
  state,
  getters
};
