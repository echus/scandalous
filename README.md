#![scan_bg_80.png](https://bitbucket.org/repo/doeRBx/images/1974197745-scan_bg_80.png)
## Scanalysis for WSC 2015

## Device addresses and channels quick reference
| Address | Node |
|---------|------|
| 50, 51 | Current integrator |
| 70 | GPS |

### Current integrator
| Channel | Info |
|---------|------|
| OUT: 0  | Current |
| OUT: 1  | Voltage |
| OUT: 2  | Power |
| OUT: 3  | Integrated current |
| OUT: 4  | Integrated power |
| OUT: 5  | Samples |
| IN: 1   | Reset integration |

## References
* See UML [here](https://bitbucket.org/repo/doeRBx/images/3660329396-scanalysis_uml.png).
* For a complete list of device addresses see [here](https://github.com/sunswift/scandal/blob/master/include/scandal/addresses.h), for channels see [here](https://github.com/sunswift/scandal/blob/master/include/scandal/devices.h).

For more details see the Scandalous wiki on Confluence.
