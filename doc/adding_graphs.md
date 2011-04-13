# Adding graphs

Circus provides two methods for adding graphs, both of which use a json file
as a graph template, but they have slightly different behaviors.

The first method, add_graph_bulk, is designed for graphs that contain metrics
from a single check and which you want to add many graphs for multiple checks.

The second method, add_graph, is designed for more complex situations where
you either want to do a one-off adding of a graph, or where the graph spans
multiple checks.

## Graph Templates

Both graph commands make use of graph templates. These are json files
specifying the graph definition, where some values are replaced by
placeholders.

The simplest way to make a template is by running the dump_graph command:

    circus dump_graph 01234567-0123-4567-a890-123456789012

Replace the UUID above with the id of a graph you want to base template on.
The UUID is the random string at the end of the URL when viewing a graph in
circonus.

This will give something that looks similar to the following:

    {
        "style": "area",
        "title": "Sample Graph",
        "datapoints": [
            {
                "derive": false,
                "metric_name": "sample_metric",
                "color": "#33aa33",
                "check_id": 1234,
                "metric_type": "numeric",
                "hidden": false,
                "axis": "l",
                "name": "Sample metric for 127.0.0.1"
            }
        ]
    }

This output is for a specific graph. In order to make it into a template, you
will need to add placeholders. Save this output to a text file (e.g.
`sample.json`) and edit it.

Placeholders are of the form `{placeholder_name}` (for example `{check_id}` or
`{group1}`).

## add_graph_bulk

When making a template suitable for use with `add_graph_bulk`, you should
always replace any check id field in the template with the `{check_id}`
placeholder.

You will probably also want to add one or more `{group1}`, `{group2}`
placeholders also. These will be replaced with data from the name of the
check, such as a hostname.

The `add_graph_bulk` command looks like:

    circus add_graph_bulk template_name 'regex pattern'

The template name points to the json template created earlier. This can either
be in the current directory or point to one of the predefined templates in the
circus templates directory.

The pattern is a regular expression and will be used to find matching checks.
For example, if the pattern was `'(.*)\.example\.com CPU'` it would find the
CPU checks for foo.example.com, bar.example.com and so on, assuming you named
your checks in such a fashion.

One important thing to note - if you have matching groups (such as the part in
parentheses above), then the values of `{group1}`, `{group2}` and so on will
be filled in with values of those matches. In the example above, `{group1}`
will be set to 'foo', 'bar' and so on. Adding the placeholders for matching
groups to your template allows you to have graph titles and legend names be
based on the check name.

### Example

You have 3 checks, called:

 * server1.example.com CPU usage
 * server2.example.com CPU usage
 * server3.example.com CPU usage

Each of these checks has a metric called `Core::Cpu\`local\`user` (this metric
name is from Resmon 2).

You have previously created a graph for 'foo.example.com CPU usage' and wish
to use that as the basis for the graph template. This graph can be viewed with
the following URL: https://circonus.com/account/example/trending/graphs/view/12345678-9abc-def0-1234-56789abcdef0

First, export the graph for foo.example.com:

    circus dump_graph 12345678-9abc-def0-1234-56789abcdef0 > example_cpu.json

The file example_cpu.json will look something like:

    {
        "style": "area",
        "title": "foo user CPU",
        "datapoints": [
            {
                "derive": false,
                "metric_name": "Core::Cpu\`local\`user",
                "color": "#33aa33",
                "check_id": 1234,
                "metric_type": "numeric",
                "hidden": false,
                "axis": "l",
                "name": "foo user CPU (%)"
            }
        ]
    }

Most of this will be identical for all graphs, but there are a few things that
will be different: the metric name, the check ID, and the name of the
datapoint that is shown on the legend. In the case of the graph name and the
datapoint name, only the hostname of the system is different (in all cases
it's a CPU graph), so we can make use of the `{group1}` placeholder. The check
ID of 1234 can be replaced with `{check_id}`. The edited template should look
like:

    {
        "style": "area",
        "title": "{group1} user CPU",
        "datapoints": [
            {
                "derive": false,
                "metric_name": "Core::Cpu\`local\`user",
                "color": "#33aa33",
                "check_id": "{check_id}",
                "metric_type": "numeric",
                "hidden": false,
                "axis": "l",
                "name": "{group1} user CPU (%)"
            }
        ]
    }


Now the template is complete, the new graphs can be added:

    $ circus add_graph_bulk example_cpu.json '(.*).example.com CPU usage'

    * Retrieving matching checks
    * Verifying that checks have the correct metrics
    5/5
    * About to add example_cpu graphs for the following checks:
    *     server1.example.com (Ashburn, VA, US)
    *     server2.example.com (Ashburn, VA, US)
    *     server3.example.com (Ashburn, VA, US)
    OK to continue? (y/n) y
    * Adding graph: server1 user CPU...Success
    * Adding graph: server2 user CPU...Success
    * Adding graph: server3 user CPU...Success

Note that if you have a template with `{group1}` or similar in it and you do
not have any matching groups in the regular expression on the command line,
then you will get an error when trying to add graphs.

## add_graph

This command only adds one graph at a time. Unlike the add_graph_bulk, all
placeholder parameters are specified on the command line in the form
`name=value`.

Example:

    circus add_graph http hostname=foo client=bar

This type of check is useful if you have a graph that covers multiple check
IDs. An example of this would be the Core::Pf::Labels check in resmon2 where
there are multiple metrics, one for each label, but they all use the same
check. If you wanted multiple graphs, one for each label, then you can use a
template with the same check ID, but have placeholders for the metric name
(changing only the label).

### example

You have an OpenBSD firewall with a check that measures traffic by PF label.
The check returns metrics like the following:

    Core::Pf::Labels`web`bytes_in
    Core::Pf::Labels`web`bytes_out
    Core::Pf::Labels`mail`bytes_in
    Core::Pf::Labels`mail`bytes_out
    Core::Pf::Labels`foo`bytes_in
    Core::Pf::Labels`foo`bytes_out
    Core::Pf::Labels`bar`bytes_in
    Core::Pf::Labels`bar`bytes_out

Where web, mail, foo, bar are labels in PF. All of these are in a single
check, in this example the check_id is 1234.

First, create the graph for one of these labels (with bytes_in/bytes_out)
manually in the web interface and export it using the dump_graph command:

    circus dump_graph 12345678-9abc-def0-1234-56789abcdef0 > example.json

It will look something like:

    {
        "style": "area",
        "title": "web bandwidth",
        "datapoints": [
            {
                "data_formula": "8,*",
                "name": "web traffic in",
                "check_id": 1234,
                "legend_formula": "auto,2,round",
                "color": "#4a00dc",
                "derive": "counter",
                "metric_type": "numeric",
                "metric_name": "Core::Pf::Labels`web`bytes_out",
                "hidden": false,
                "stack": 1,
                "axis": "l"
            },
            {
                "data_formula": "-8,*",
                "name": "web traffic in",
                "check_id": 1234,
                "legend_formula": "-1,*,auto,2,round",
                "color": "#33aa33",
                "derive": "counter",
                "metric_type": "numeric",
                "metric_name": "Core::Pf::Labels`web`bytes_in",
                "hidden": false,
                "axis": "l"
            }
        ]
    }

Next you need to turn it into a template. The only thing that changes between
graphs is the label used, in this case 'web'. This is used in the metric name,
graph title, and datapoint names. Any name can be used for the placeholder. In
this example, `{label}` is used:

    {
        "style": "area",
        "title": "{label} bandwidth",
        "datapoints": [
            {
                "data_formula": "8,*",
                "name": "{label} traffic in",
                "check_id": 1234,
                "legend_formula": "auto,2,round",
                "color": "#4a00dc",
                "derive": "counter",
                "metric_type": "numeric",
                "metric_name": "Core::Pf::Labels`{label}`bytes_out",
                "hidden": false,
                "stack": 1,
                "axis": "l"
            },
            {
                "data_formula": "-8,*",
                "name": "{label} traffic in",
                "check_id": 1234,
                "legend_formula": "-1,*,auto,2,round",
                "color": "#33aa33",
                "derive": "counter",
                "metric_type": "numeric",
                "metric_name": "Core::Pf::Labels`{label}`bytes_in",
                "hidden": false,
                "axis": "l"
            }
        ]
    }

To add graphs with different labels, run add_graph with this template:

    circus add_graph example.json label=mail
    circus add_graph example.json label=foo
    circus add_graph example.json label=bar

If you want to automate this for many graphs, use a for loop in bash:

    for i in mail foo bar; do
        circus add_graph example.json label=$i
    done

Note that because we didn't change the check id between graphs, that this
was just hardcoded in the template. If you wanted, you could create a
placeholder for the check_id and require that it be specified on the command
line. If this was done, the add_graph command would look like:

    circus add_graph example.json label=mail check_id=1234

<!-- vim: ft=markdown
-->
