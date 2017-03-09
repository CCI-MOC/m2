<h2>BMI API test</h2>

<table>
  <tbody>
    <tr>
      <th>Ceph API</th>
      <th align="center">Arguments</th>
      <th align="right">Comments</th>
    </tr>
    <tr>
    <td>open_images</td>
      <td align="">
        <ul>
          <li>img_id</li>
          <li>img_size</li>
        </ul>
      </td>
      <td align=""></td>
    </tr>
    <tr>
      <td>list_images</td>
      <td align=""></td>
      <td align=""></td>
    </tr>
    <tr>
      <td>create_image</td>
      <td align="">
        <ul>
          <li>img_id</li>
          <li>img_size</li>
        </ul>
      </td>
      <td align=""></td>
    </tr>
    <tr>
      <td>clone</td>
      <td align="">
        <ul>
          <li>parent_img_name</li>
          <li>parent_snap_name</li>
          <li>clone_img_name</li>
        </ul>
      </td>
      <td align=""></td>
    </tr>
    <tr>
      <td>remove</td>
      <td align="">img_id</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>write</td>
        <td align="">
          <ul>
            <li>img_id</li>
            <li>data</li>
            <li>offset</li>
          </ul>
        </td>
        <td align=""></td>
      </tr>
    <tr>
      <td>snap_image</td>  
        <td align="">
          <ul>
            <li>img_id</li>
            <li>name</li>
          </ul>
        </td>
      <td align=""></td>
    </tr>
    <tr>
      <td>snap_protect</td>     
      <td align="">
        <ul>
          <li>img_id</li>
          <li>snap_name</li>
        </ul>
      </td>
      <td align=""></td>
    </tr>
    <tr>
      <td>snap_unprotect</td>
      <td align="">
        <ul>
          <li>img_id</li>
          <li>snap_name</li>
        </ul>
      </td>
      <td align=""></td>
    </tr>
    <tr>
      <td>flatten</td>
      <td align="">img_id</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>list_snapshots</td>
      <td align="">img_id</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>remove_snapshot</td>
      <td align="">
        <ul>
          <li>img_id</li>
          <li>name</li>
        </ul>
      </td>
      <td align=""></td>
    </tr>
    <tr>
      <td>get_image</td>
      <td align="">img_id</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>get_parent_info</td>
      <td align="">img_id</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>map</td>
      <td align="">ceph_img_name</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>unmap</td>
      <td align="">rbd_name</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>showmapped</td>
      <td align=""></td>
      <td align=""></td>
    </tr>
    
    <!--<tr>
      <td>
        <ul>
          <li>item1</li>
          <li>item2</li>
        </ul>
      </td>
      <td align=""></td>
      <td align=""></td>
    </tr>-->
  </tbody>
</table>

<table>
  <tbody>
    <tr>
      <th>IET API</th>
      <th align="center">Arguments</th>
      <th align="right">Comments</th>
    </tr>
    <tr>
      <td>add_target</td>
      <td align="">ceph_img_name</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>remove_target</td>
      <td align="">ceph_img_name</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>list_targets</td>
      <td align=""></td>
      <td align=""></td>
    </tr>
    <tr>
      <td>__add_mapping</td>
      <td align="">
        <ul>
          <li>ceph_img_name</li>
          <li>rbd_name</li>
        </ul>
      </td>
      <td align=""></td>
    </tr>
    <tr>
      <td>__remove_mapping</td>
      <td align="">
        <ul>
          <li>ceph_img_name</li>
          <li>rbd_name</li>
        </ul>
      </td>
      <td align=""></td>
    </tr>
    <tr>
      <td>__check_status</td>
      <td align=""></td>
      <td align=""></td>
    </tr>
    <tr>
      <td>persist_targets</td>
      <td align=""></td>
      <td align=""></td>
    </tr>
  </tbody>
</table>

<table>
  <tbody>
    <tr>
      <th>TGT API</th>
      <th align="center">Arguments</th>
      <th align="right">Comments</th>
    </tr>
    <tr>
      <td>show_status</td>
      <td align=""></td>
      <td align=""></td>
    </tr>
    <tr>
      <td>__generate_config_file</td>
      <td align="">target_name</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>add_target</td>
      <td align="">target_name</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>remove_target</td>
      <td align="">target_name</td>
      <td align=""></td>
    </tr>
    <tr>
      <td>list_targets</td>
      <td align=""></td>
      <td align=""></td>
    </tr>
  </tbody>
</table>
