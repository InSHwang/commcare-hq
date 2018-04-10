hqDefine('reports_core/js/base_template_new', function() {
        var base_url = "{{ url }}";
        function get_report_url() {
            return base_url;
        }
    $(function() {
        var charts = hqImport('reports_core/js/charts');
        var chartSpecs = {{ report.spec.charts|JSON }};
        var updateCharts = function (data) {
            if (chartSpecs !== null && chartSpecs.length > 0) {
                var isReportBuilderReport = {{ report.spec.report_meta.created_by_builder|JSON }};
                if (data.iTotalRecords > 25 && isReportBuilderReport) {
                    $("#chart-warning").removeClass("hide");
                    charts.clear($("#chart-container"));
                } else {
                    $("#chart-warning").addClass("hide");
                    charts.render(chartSpecs, data.aaData, $("#chart-container"));
                }
            }
        };

        var mapSpec = {{ report.spec.map_config|JSON }};
        var updateMap = function (data) {
            if (mapSpec) {
                mapSpec.mapboxAccessToken = '{{ MAPBOX_ACCESS_TOKEN }}';
                var render_map = hqImport('reports_core/js/maps').render;
                render_map(mapSpec, data.aaData, $("#map-container"));
            }
        };

        var paginationNotice = function (data) {
            if (mapSpec) {  // Only show warning for map reports
                if (data.aaData !== undefined && data.iTotalRecords !== undefined) {
                    if (data.aaData.length < data.iTotalRecords) {
                        $('#info-message').html(
                            "{% trans 'Showing the current page of data. Switch pages to see more data.' %}"
                        );
                        $('#report-info').removeClass('hide');
                    } else {
                        $('#report-info').addClass('hide');
                    }
                }
            }
        };

        var errorCallback = function (jqXHR, textStatus, errorThrown) {
            $('#error-message').html(errorThrown);
            $('#report-error').removeClass('hide');
        };

        var successCallback = function(data) {
            if(data.error) {
                $('#error-message').html(data.error);
                $('#report-error').removeClass('hide');
            } else {
                $('#report-error').addClass('hide');
            }
            if (data.warning) {
                $('#warning-message').html(data.warning);
                $('#report-warning').removeClass('hide');
            } else {
                $('#report-warning').addClass('hide');
            }
        };

        var reportTables = hqImport("reports/js/config.dataTables.bootstrap").HQReportDataTables({
            dataTableElem: '#report_table_{{ report.slug }}',
            defaultRows: {{ report_table.default_rows|default:10 }},
            startAtRowNum: {{ report_table.start_at_row|default:0 }},
            showAllRowsOption: {{ report_table.show_all_rows|JSON }},
            aaSorting: [],
            {% if headers.render_aoColumns %}aoColumns: {{ headers.render_aoColumns|JSON }},{% endif %}
            autoWidth: {{ headers.auto_width|JSON }},
            {% if headers.custom_sort %}customSort: {{ headers.custom_sort|JSON }},{% endif %}

            ajaxSource: '{{ url }}',
            ajaxMethod: '{{ method }}',
            ajaxParams: function() {
                return $('#paramSelectorForm').serializeArray();
            },
            {% if report_table.left_col.is_fixed %}
                fixColumns: true,
                fixColsNumLeft: {{ report_table.left_col.fixed.num }},
                fixColsWidth: {{ report_table.left_col.fixed.width }},
            {% endif %}
            successCallbacks: [successCallback, updateCharts, updateMap, paginationNotice],
            errorCallbacks: [errorCallback]
        });
        $('#paramSelectorForm').submit(function(event) {
            $('#reportHint').remove();
            $('#reportContent').removeClass('hide');
            event.preventDefault();
            reportTables.render();
        });
        // after we've registered the event that prevents the default form submission
        // we can enable the submit button
        $("#apply-filters").prop('disabled', false);

        $(function() {
            $('.header-popover').popover({
                trigger: 'hover',
                placement: 'bottom',
                container: 'body'
            });
        });

    });

    $(function () {
        // add any filter javascript dependencies
        {% for filter in report.filters %}
            {% if filter.javascript_template %}
                {% include filter.javascript_template with filter=filter context_=filter_context|dict_lookup:filter.css_id %}
            {% endif %}
        {% endfor %}
    });
});
