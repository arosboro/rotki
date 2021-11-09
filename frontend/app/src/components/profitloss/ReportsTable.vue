<template>
  <v-card>
    <v-card-title>
      <card-title> {{ $t('profit_loss_reports.title') }}</card-title>
    </v-card-title>
    <v-card-text>
      <v-sheet outlined rounded>
        <data-table
          show-expand
          single-expand
          sort-by="created"
          item-key="identifier"
          :items="index.reports"
          :headers="headers"
        >
          <template #item.name="{ item }">
            {{ item.name }}
          </template>
          <template #item.created="{ item }">
            <date-display :timestamp="item.created" />
          </template>
          <template #item.start="{ item }">
            <date-display :timestamp="item.start" />
          </template>
          <template #item.end="{ item }">
            <date-display :timestamp="item.end" />
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
import { ReportCache } from '@rotki/common/lib/reports';
import { Component, Mixins } from 'vue-property-decorator';
import { DataTableHeader } from 'vuetify';
import { mapActions, mapGetters, mapState } from 'vuex';
import DataTable from '@/components/helper/DataTable.vue';
import CardTitle from '@/components/typography/CardTitle.vue';
import StatusMixin from '@/mixins/status-mixin';
import { ReportActions } from '@/store/reports/const';

@Component({
  components: {
    DataTable,
    CardTitle
  },
  computed: {
    ...mapGetters('reports', ['reports']),
    ...mapState('reports', ['index'])
  },
  methods: {
    ...mapActions('reports', [ReportActions.FETCH_REPORTS])
  }
})
export default class ReportsTable extends Mixins(StatusMixin) {
  page!: number;
  pages!: number;
  rows!: number;
  records!: number;
  reports!: ReportCache[];
  headers: DataTableHeader[] = [
    {
      text: this.$t('profit_loss_reports.columns.name').toString(),
      value: 'name'
    },
    {
      text: this.$t('profit_loss_reports.columns.created').toString(),
      value: 'created'
    },
    {
      text: this.$t('profit_loss_reports.columns.start').toString(),
      value: 'start'
    },
    {
      text: this.$t('profit_loss_reports.columns.end').toString(),
      value: 'end'
    },
    {
      text: this.$t('profit_loss_reports.columns.size').toString(),
      value: 'sizeOnDisk'
    }
  ];
  [ReportActions.FETCH_REPORTS]!: (refresh: boolean) => Promise<void>;

  async refresh() {
    await this[ReportActions.FETCH_REPORTS](true);
  }

  async mounted() {
    await this[ReportActions.FETCH_REPORTS](false);
  }
}
</script>
