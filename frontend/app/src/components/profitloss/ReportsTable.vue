<template>
  <v-card>
    <v-card-title>
      <card-title> {{ $t('profit_loss_reports.title') }}</card-title>
    </v-card-title>
    <v-card-text>
      <v-sheet outlined rounded>
        <data-table
          :headers="headers"
          :items="entries"
          show-expand
          single-expand
          sort-by="timestamp"
          item-key="identifier"
        >
          <template #item.name="{ item }">
            {{ item.name }}
          </template>
          <template #item.timestamp="{ item }">
            {{ item.timestamp }}
          </template>
          <template #item.startTs="{ item }">
            <date-display :timestamp="item.startTs" />
          </template>
          <template #item.endTs="{ item }">
            <date-display :timestamp="item.endTs" />
          </template>
          <template #item.sizeOnDisk="{ item }">
            {{ item.sizeOnDisk }}
          </template>
        </data-table>
      </v-sheet>
    </v-card-text>
  </v-card>
</template>

<script lang="ts">
import { PagedResourceParameters } from '@rotki/common';
import { PagedReport } from '@rotki/common/lib/reports';
import {
  computed,
  defineComponent,
  onBeforeMount,
  Ref,
  ref
} from '@vue/composition-api';
import { DataTableHeader } from 'vuetify';
import DataTable from '@/components/helper/DataTable.vue';
import CardTitle from '@/components/typography/CardTitle.vue';
import { setupStatusChecking } from '@/composables/common';
import i18n from '@/i18n';
import { Section } from '@/store/const';
import { ReportActions } from '@/store/reports/const';
import { RotkehlchenState } from '@/store/types';
import { useStore } from '@/store/utils';

export default defineComponent({
  name: 'ReportsTable',
  components: {
    DataTable,
    CardTitle
  },
  setup() {
    const selected: Ref<string[]> = ref([]);
    const store = useStore();

    const state: RotkehlchenState = store.state;
    const itemsPerPage = state.settings!!.itemsPerPage;

    const payload = ref<PagedResourceParameters>({
      limit: itemsPerPage,
      offset: 0,
      orderByAttribute: 'created',
      ascending: false
    });

    const entries = computed(() => {
      const state: RotkehlchenState = store.state;
      return state.reports!!.index.entries;
    });
    const limit = computed(() => {
      const state: RotkehlchenState = store.state;
      return state.reports!!.index.entriesLimit;
    });
    const found = computed(() => {
      const state: RotkehlchenState = store.state;
      return state.reports!!.index.entriesFound;
    });
    const total = computed(() => {
      const state: RotkehlchenState = store.state;
      return state.reports!!.index.entriesTotal;
    });

    const fetchReports = async (refresh: boolean = false) => {
      await store.dispatch(`reports/${ReportActions.FETCH_REPORTS}`, {
        ...payload.value,
        onlyCache: !refresh
      });
    };
    const refresh = async () => await fetchReports(true);
    const onPaginationUpdate = ({
      ascending,
      page,
      sortBy,
      itemsPerPage
    }: {
      page: number;
      itemsPerPage: number;
      sortBy: keyof PagedReport;
      ascending: boolean;
    }) => {
      const offset = (page - 1) * itemsPerPage;
      payload.value = {
        ...payload.value,
        orderByAttribute: sortBy,
        offset,
        limit: itemsPerPage,
        ascending
      };
      fetchReports().then();
    };

    onBeforeMount(async () => await fetchReports());

    const { isSectionRefreshing, shouldShowLoadingScreen } =
      setupStatusChecking();

    return {
      entries,
      limit,
      total,
      found,
      loading: shouldShowLoadingScreen(Section.REPORTS),
      refreshing: isSectionRefreshing(Section.REPORTS),
      refresh,
      selected,
      fetchReports,
      onPaginationUpdate
    };
  },
  data: function () {
    return {
      headers: (() => {
        const headers: DataTableHeader[] = [
          {
            text: i18n.t('profit_loss_reports.columns.name').toString(),
            value: 'name'
          },
          {
            text: i18n.t('profit_loss_reports.columns.created').toString(),
            value: 'created'
          },
          {
            text: i18n.t('profit_loss_reports.columns.start').toString(),
            value: 'start'
          },
          {
            text: i18n.t('profit_loss_reports.columns.end').toString(),
            value: 'end'
          },
          {
            text: i18n.t('profit_loss_reports.columns.size').toString(),
            value: 'sizeOnDisk'
          }
        ];
        return headers;
      })()
    };
  }
});
</script>
