BMI test cases
For now, we have BMI rest API
Commands:
<table>
  <tr>
    <th>Option</th>
    <th>Description</th>
  </tr>
  <tr>
  <td><b>cp</b></td>
    <td>Copy an existing image not clones</td>
  </tr>
  <tr>
  <td><b>db</b></td>
    <td>DB Related Commands</td>
  </tr>
  <tr>
  <td><b>download</b></td>
    <td>Download Image from BMI</td>
  </tr>
  <tr>
  <td><b>dpro</b></td>
    <td>Deprovision a node</td>
  </tr>
  <tr>
  <td><b>export</b></td>
    <td>Export a BMI image to ceph</td>
  </tr>
  <tr>
  <td><b>import</b></td>
    <td>Import an Image or Snapshot into BMI</td>
  </tr>
  <tr>
  <td><b>iscsi</b></td>
    <td>ISCSI Related Commands</td>
  </tr>
  <tr>
  <td><b>ls</b></td>
    <td>List Images Stored</td>
  </tr>
  <tr>
  <td><b>mv</b></td>
    <td>Move Image From Project to Another</td>
  </tr>
  <tr>
  <td><b>node</b></td>
    <td>Node Related Commands</td>
  </tr>
  <tr>
  <td><b>pro</b></td>
    <td>Provision a Node</td>
  </tr>
  <tr>
  <td><b>project</b></td>
    <td>Project Related Commands</td>
  </tr>
  <tr>
  <td><b>rm</b></td>
    <td>Remove an Image</td>
  </tr>
  <tr>
  <td><b>showpro</b></td>
    <td>Lists Provisioned Nodes</td>
  </tr>
  <tr>
  <td><b>snap</b></td>
    <td>Snapshot Related Commands</td>
  </tr>
  <tr>
  <td><b>upload</b></td>
    <td>Upload Image to BMI</td>
  </tr>
</table>

We design test cases based on APIs we have. 

<ol>
  <li>cp
    <ul>
      <li>bmi cp [OPTIONS] SRC_PROJECT IMG1 DEST_PROJECT IMG2</li>
    </ul>
  </li>
  <li>db
    <ul>
      <li>bmi db create [OPTIONS] PROJECT IMG</li>
      <li>bmi db ls</li>
      <li>bmi db rm [OPTIONS] PROJECT IMG</li>
    </ul>
  </li>
  <li>download
    <ul>
      <li>Not Yet Implemented</li>
    </ul>
  </li>
  <li>drpo
    <ul>
      <li>bmi dpro [OPTIONS] PROJECT NODE NETWORK NIC</li>
    </ul>
  </li>
  <li>export
    <ul>
      <li>bmi export [OPTIONS] PROJECT IMG NAME</li>
    </ul>
  </li>
  <li>import
    <ul>
      <li>bmi import [OPTIONS] PROJECT IMG</li>
    </ul>
  </li>
  <li>iscsi
    <ul>
      <li> (need to reimplement)</li>
      <li>bmi iscsi create [OPTIONS] PROJECT IMG</li>
      <li>bmi iscsi ls [OPTIONS] PROJECT</li>
      <li>bmi iscsi rm [OPTIONS] PROJECT IMG</li>
    </ul>
  </li>
  <li>ls
    <ul>
      <li>bmi ls [OPTIONS] PROJECT</li>
    </ul>
  </li>
  <li>mv
    <ul>
      <li>bmi mv [OPTIONS] SRC_PROJECT IMG1 DEST_PROJECT IMG2</li>
    </ul>
  </li>
  <li>node
    <ul>
      <li>bmi node ip [OPTIONS] PROJECT NODE</li>
    </ul>
  </li>
  <li> pro
    <ul>
      <li>bmi pro [OPTIONS] PROJECT NODE IMG NETWORK NIC</li>
    </ul>
  </li>
  <li>bmi project
    <ul>
      <li>bmi project create [OPTIONS] PROJECT NETWORK</li>
      <li>bmi project ls</li>
      <li>bmi project rm [OPTIONS] PROJECT</li>
    </ul>
  </li>
  <li>rm
    <ul>
      <li>bmi rm [OPTIONS] PROJECT IMG</li>
    </ul>
  </li>
  <li>showpro
    <ul>
      <li>bmi showpro [OPTIONS] PROJECT</li>
    </ul>
  </li>
  <li>snap
    <ul>
      <li>bmi snap create [OPTIONS] PROJECT NODE SNAP_NAME</li>
      <li>bmi snap ls [OPTIONS] PROJECT</li>
      <li>bmi snap rm [OPTIONS] PROJECT SNAP_NAME</li>
    </ul>
  </li>
  <li>upload
    <ul>
      <li>Not Yet Implemented</li>
    </ul>
  </li>
</ol>
