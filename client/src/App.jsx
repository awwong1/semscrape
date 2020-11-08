import React from "react"
import { Pane, Text, Heading } from 'evergreen-ui'
import ControlPanel from "./ControlPanel"

const App = () => <div className="App">
  <Pane display="flex" justifyContent="space-between" padding={16} background="tint2" borderRadius={3}>
    <Pane alignItems="center" display="flex">
      <Heading size={900} paddingRight={10}>Semscrape</Heading>
    </Pane>
    <Pane alignItems="center" display="flex">
      <Text>A Muck Rack takehome assessment, by <a href="https://github.com/awwong1">@awwong1</a></Text>
    </Pane>
  </Pane>
  <ControlPanel />
</div>

export default App;
