<template>
  <div>
    <v-container fluid class="pa-0 d-flex flex-column justify-center align-center" style="min-height: 600px; width: 100%">

      <labels_manager_tabs
        style="min-height: 500px; width: 85%"
        width="100%"
        :project_string_id="project_string_id"
        :current_schema="schema"
      ></labels_manager_tabs>

    </v-container>
    <wizard_navigation
      @next="go_to_step(3)"
      @skip="go_to_step(3)"
      @back="$emit('back')">
    </wizard_navigation>
  </div>




  <!--  <v-layout class="pa-0 d-flex flex-column" style="min-height: 600px">-->

<!--    <v-layout>-->
<!--      <v-row>-->

<!--        <v-col cols="6">-->
<!--          <div class="d-flex align-center ">-->
<!--            <h2 class="font-weight-medium text&#45;&#45;primary flex-grow-1">Labels:</h2>-->
<!--            <v-btn color="primary" icon @click="fetch_labels"><v-icon>mdi-refresh</v-icon></v-btn>-->

<!--            <button_with_menu-->
<!--              datacy="new_label_template"-->
<!--              button_text="Create Label"-->
<!--              tooltip_message="Create Label"-->
<!--              @click="$store.commit('set_user_is_typing_or_menu_open', true)"-->
<!--              @update:return-value="$store.commit('set_user_is_typing_or_menu_open', false)"-->
<!--              icon="add"-->
<!--              :icon_style="false"-->
<!--              :large="true"-->
<!--              :left="true"-->
<!--              icon_color="white"-->
<!--              :close_by_button="true"-->
<!--              color="primary"-->
<!--              offset="x"-->
<!--            >-->

<!--              <template slot="content"-->
<!--                        slot-scope="props">-->

<!--                <v_labels_new @label_created="on_label_created"-->
<!--                              :schema_id="schema.id"-->
<!--                              :menu_open="props.menu_open">-->
<!--                </v_labels_new>-->

<!--              </template>-->

<!--            </button_with_menu>-->
<!--          </div>-->

<!--          <labels_management_list-->
<!--            :project_string_id="project_string_id"-->
<!--            :label_file_list="label_file_list"-->
<!--            @label_file_list_updated="on_label_file_list_updated"-->
<!--          >-->
<!--          </labels_management_list>-->

<!--        </v-col>-->
<!--        <v-col cols="6" style="border-left: 1px solid #b9d1ec" class="d-flex flex-column">-->
<!--          <attribute_group_list_manager-->
<!--            v-if="project_string_id"-->
<!--            :schema_id="schema.id"-->
<!--            ref="attribute_group_list_manager"-->
<!--            :show_borders="true"-->
<!--            :project_string_id="project_string_id"-->
<!--            :mode = "'edit'"-->
<!--            :show_empty_placeholder="true"-->
<!--            @attribute_group_list_updated="on_attribute_group_list_updated"-->
<!--          >-->
<!--          </attribute_group_list_manager>-->

<!--        </v-col>-->
<!--      </v-row>-->

<!--    </v-layout>-->

<!--    <wizard_navigation-->
<!--      @next="go_to_step(3)"-->
<!--      @skip="go_to_step(3)"-->
<!--      @back="$emit('back')"-->
<!--      :disabled_next="label_file_list.length == 0 && attribute_group_list.length === 0">-->
<!--    </wizard_navigation>-->
<!--  </v-layout>-->

</template>

<script lang="ts">

  import axios from '../../services/customInstance';
  import Vue from "vue";
  import v_labels_edit from '../annotation/labels_edit'
  import labels_manager_tabs from './labels_manager_tabs'
  import attribute_group_list_manager from '../attribute/attribute_group_list_manager'
  import labels_management_list from '../label/labels_management_list'
  import {get_labels} from '../../services/labelServices';

  export default Vue.extend({
      name: 'labels_attributes_manager',
      components:{
        attribute_group_list_manager,
        labels_manager_tabs,
        labels_management_list,
        v_labels_edit,
      },
      props: {
        'project_string_id': {},
        'schema': {
          required: true
        },
      },
      watch: {},
      async mounted() {
        await this.fetch_labels();

      },
      data() {
        return {

          openedPanel: false,
          label_file_list: [],
          attribute_group_list: [],
          label_file_colour_map: {}
        }
      },

      methods: {
        on_attribute_group_list_updated: function(new_attr_list){
          this.attribute_group_list = new_attr_list;
        },
        update_attributes_label_file_list: function(new_label_file_list){
          this.$refs.attribute_group_list_manager.update_label_file_list_for_all_attributes(new_label_file_list)
        },
        on_label_file_list_updated: function(new_label_file_list){
          this.label_file_list = new_label_file_list;
          this.update_attributes_label_file_list(new_label_file_list)
        },
        on_label_created: function(label_file){
          this.label_file_list.push(label_file);
          this.update_attributes_label_file_list(this.label_file_list)
        },
        go_to_step: function(step){
          this.$emit('skip', step)
        },
        fetch_labels: async function(){
          if (this.project_string_id == null) {
            return
          }
          this.label_refresh_loading = true
          let [result, error] = await get_labels(this.project_string_id, this.$props.schema.id)
          if(error){
            return
          }
          if(result){

            this.label_file_list = result.labels_out

            this.label_file_colour_map = result.label_file_colour_map

            this.label_refresh_loading = false
            this.$emit('labels_fetched', this.label_file_list)
          }
          this.labels_loading = false
        },

        open_panel_by_id(id: number){
          if (!this.attribute_group_list) {return }
          this.openedPanel = this.attribute_group_list.findIndex(x => {
            return x.id == id
          })
        },

      }
    }
  ) </script>

<style scoped>

  .skip-title{
    color: #1565c0 !important;
  }
  .skip-title:hover{
    cursor: pointer;
  }
</style>
