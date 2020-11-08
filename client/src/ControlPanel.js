/* eslint-disable react/prop-types */
import React from "react"
import { Badge, HeartIcon, LinkIcon, TimelineEventsIcon, UserIcon, Heading, Table, Spinner, Pane, SearchInput, Button, SideSheet, Text } from "evergreen-ui"

class ControlPanel extends React.Component {

    constructor(props) {
        super(props)
        this.state = {
            loading: true,
            count: 0,
            results: [],
            next: null,

            // sidesheet logic
            showSideSheet: false,
            articleDetails: null,
        }

        this.searchRef = React.createRef()
    }

    componentDidMount = () => {
        fetch("/search/articles/?ordering=-publication_date&format=json&limit=30")
            .then(response => response.json())
            .then(({ count, next, results }) => {
                this.setState({ count, next, results })
            })
            .catch(console.error)
            .finally(() => this.setState({ loading: false }))
    }

    handleSubmitSearch = (e) => {
        e.preventDefault()
        // https://github.com/segmentio/evergreen/issues/508
        // innerRef no longer supported, therefore do ref and get lastChild
        const rawQuery = this.searchRef.current.lastChild.value
        if (rawQuery) {
            this.setState({ loading: true, count: 0, next: null, results: [] })
            const searchQuery = encodeURI(rawQuery)
            fetch(`/search/articles/?search=${searchQuery}&ordering=-publication_date&format=json&limit=30`)
                .then(response => response.json())
                .then(({ count, next, results }) => {
                    this.setState({ count, next, results })
                })
                .catch(console.error)
                .finally(() => this.setState({ loading: false }))
        }
    }

    handleLoadNext = () => {
        this.setState({ loading: true })
        fetch(this.state.next)
            .then(response => response.json())
            .then(({ count, next, results: newResults }) => {
                console.log(count, next, newResults)
                this.setState({ count, next, results: [...this.state.results, ...newResults] })
            })
            .catch(console.error)
            .finally(() => this.setState({ loading: false }))

    }

    render = () => <>
        <Pane paddingY={14} position="sticky" top={0}>
            <form onSubmit={this.handleSubmitSearch}>
                <Pane display="flex" padding={4} background="tint2" elevation={1}>
                    <SearchInput
                        width="100%"
                        placeholder="Find articles..."
                        ref={this.searchRef}
                    />
                    <Button appearance="primary">Search</Button>
                </Pane>
            </form>
        </Pane>

        <SideSheet
            isShown={this.state.showSideSheet}
            onCloseComplete={() => this.setState({ showSideSheet: false })}
        >
            <ArticleDetails article={this.state.articleDetails} />
        </SideSheet>
        <Table onScroll={this.handleScroll}>
            <Table.Head>
                <Table.TextHeaderCell flexShrink={0} flexGrow={1}>
                    Title
                </Table.TextHeaderCell>
                <Table.TextHeaderCell>
                    URL
                </Table.TextHeaderCell>
                <Table.TextHeaderCell>
                    Overall Sentiment
                </Table.TextHeaderCell>
            </Table.Head>
            <Table.Body>
                {this.state.results.map(result => {
                    // overall sentiment string
                    let sentiment = result.overall_sentiment.label
                    let rowIntent = "none"
                    if (sentiment === "POSITIVE") {
                        rowIntent = "success"
                    } else if (sentiment === "NEGATIVE") {
                        rowIntent = "danger"
                    }
                    if (result.overall_sentiment.avg !== null) {
                        sentiment += ` ${result.overall_sentiment.avg.toFixed(3)}`
                    }

                    return <Table.Row
                        key={result.id}
                        isSelectable
                        intent={rowIntent}
                        onSelect={() => this.setState({ showSideSheet: true, articleDetails: result })}
                    >
                        <Table.TextCell flexShrink={0} flexGrow={1}>{result.title}</Table.TextCell>
                        <Table.TextCell>{result.url}</Table.TextCell>
                        <Table.TextCell>{sentiment}</Table.TextCell>
                    </Table.Row>
                })}
            </Table.Body>
        </Table>
        {!this.state.loading && <Pane display="flex" justifyContent="center">
            <Text>Loaded {this.state.results.length} of {this.state.count} articles.</Text>
        </Pane>}
        <Pane display="flex" alignItems="center" justifyContent="center" height={200}>
            {this.state.loading && <Spinner />}
            {(!this.state.loading && this.state.next) && <Button height={56} onClick={this.handleLoadNext}>Load next 30?</Button>}
            {(!this.state.loading && !this.state.next) && <Heading>All done!</Heading>}
        </Pane>
    </>
}

const ArticleDetails = ({ article }) => {
    if (article === null) {
        return <Text>Undefined</Text>
    }

    let sentimentColor = "neutral"
    if (article.overall_sentiment.label === "POSITIVE") {
        sentimentColor = "green"
    } else if (article.overall_sentiment.label === "NEGATIVE") {
        sentimentColor = "red"
    }

    let overallPositivity = ""
    if (article.overall_sentiment.avg) {
        overallPositivity += `Average Positivity ${article.overall_sentiment.avg.toFixed(3)}`
        if (article.overall_sentiment.std) {
            overallPositivity += ` ± ${article.overall_sentiment.std.toFixed(3)}`
        }
    }

    return <Pane padding={10}>
        <Pane paddingY={5}>
            <Heading size={700}><a href={article.url}>{article.title}</a></Heading>
        </Pane>
        <Pane display="flex" alignItems="center" paddingY={5}>
            <TimelineEventsIcon size={30} flexShrink={0} />
            <Text paddingLeft={5}>{article.publication_date}</Text>
        </Pane>
        <Pane display="flex" alignItems="center" paddingY={5}>
            <UserIcon size={30} flexShrink={0} />
            <Text paddingLeft={5}>
                {article.author}
                {!article.author && "Unknown"}
            </Text>
        </Pane>
        <Pane display="flex" alignItems="center" paddingY={5}>
            <LinkIcon size={30} flexShrink={0} />
            <Text paddingLeft={5}>
                <a href={article.url}>{article.url}</a>
            </Text>
        </Pane>
        <Pane display="flex" alignItems="center" paddingY={5}>
            <HeartIcon size={30} flexShrink={0} />
            <Text paddingLeft={5}>
                <Badge color={sentimentColor}>{article.overall_sentiment.label}</Badge> {overallPositivity}
            </Text>
        </Pane>

        <Table>
            <Table.Head>
                <Table.TextHeaderCell flexShrink={0} flexGrow={1}>
                    Sentence
                </Table.TextHeaderCell>
                <Table.TextHeaderCell>
                    Sentiment
                </Table.TextHeaderCell>
                <Table.TextHeaderCell>
                    Probability
                </Table.TextHeaderCell>
            </Table.Head>
            <Table.VirtualBody height={640}>
                {article.sentiment.map((payload) => {
                const bdColor = payload.sentiment.label === "POSITIVE" ? "green" : "red"
                return <Table.Row key={payload.sentence} height="auto">
                    <Table.TextCell>{payload.sentence}</Table.TextCell>
                    <Table.TextCell><Badge color={bdColor}>{payload.sentiment.label}</Badge></Table.TextCell>
                    <Table.TextCell isNumber>{payload.sentiment.score.toFixed(3)}</Table.TextCell>
                </Table.Row>})}
            </Table.VirtualBody>
        </Table>
    </Pane>
}


export default ControlPanel