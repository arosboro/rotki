<template>
  <v-card>
    <i18n tag="div" path="profit_loss_reports.title" class="text-h5 mt-6">
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
            <!--            <template #header.selection>-->
            <!--              <v-simple-checkbox-->
            <!--                :ripple="false"-->
            <!--                :value="allSelected"-->
            <!--                color="primary"-->
            <!--                @input="setSelected($report)"-->
            <!--              />-->
            <!--            </template>-->
            <!--            <template #item.selection="{ item }">-->
            <!--              <v-simple-checkbox-->
            <!--                :ripple="false"-->
            <!--                color="primary"-->
            <!--                :value="selected.includes(item.identifier)"-->
            <!--                @input="selectionChanged(item.identifier, $event)"-->
            <!--              />-->
            <!--            </template>-->
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
    </i18n>
  </v-card>
</template>

<script lang="ts">
import { ReportCache } from '@rotki/common/lib/reports';
import { Component, Mixins } from 'vue-property-decorator';
import { DataTableHeader } from 'vuetify';
import { mapActions, mapGetters, mapState } from 'vuex';
import StatusMixin from '@/mixins/status-mixin';
import { ReportActions } from '@/store/reports/const';

@Component({
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
